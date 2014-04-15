
/*
 * Copyright 2014 Jan Pazdziora
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <security/pam_appl.h>

#include "apr_strings.h"

#include "ap_config.h"
#include "ap_provider.h"
#include "httpd.h"
#include "http_config.h"
#include "http_core.h"
#include "http_log.h"
#include "http_protocol.h"
#include "http_request.h"

#include "mod_auth.h"

typedef struct {
	char * pam_service;
} authnz_pam_config_rec;

static void * create_dir_conf(apr_pool_t * pool, char * dir) {
	authnz_pam_config_rec * cfg = apr_pcalloc(pool, sizeof(authnz_pam_config_rec));
	return cfg;
}

static const command_rec authnz_pam_cmds[] = {
	AP_INIT_TAKE1("AuthPAMService", ap_set_string_slot,
		(void *)APR_OFFSETOF(authnz_pam_config_rec, pam_service),
		OR_AUTHCFG, "PAM service to authenticate against"),
	{NULL}
};

static int pam_authenticate_conv(int num_msg, const struct pam_message ** msg, struct pam_response ** resp, void * appdata_ptr) {
	struct pam_response * response = NULL;
	if (!msg || !resp || !appdata_ptr)
		return PAM_CONV_ERR;
	if (!(response = malloc(num_msg * sizeof(struct pam_response))))
		return PAM_CONV_ERR;
	int i;
	for (i = 0; i < num_msg; i++) {
		response[i].resp = 0;
		response[i].resp_retcode = 0;
		if (msg[i]->msg_style == PAM_PROMPT_ECHO_OFF) {
			response[i].resp = strdup(appdata_ptr);
		} else {
			free(response);
			return PAM_CONV_ERR;
		}
	}
	* resp = response;
	return PAM_SUCCESS;
}

#define _REMOTE_USER_ENV_NAME "REMOTE_USER"
#define _EXTERNAL_AUTH_ERROR_ENV_NAME "EXTERNAL_AUTH_ERROR"
#define _PAM_STEP_AUTH 1
#define _PAM_STEP_ACCOUNT 2
#define _PAM_STEP_ALL 3
static authn_status pam_authenticate_with_login_password(request_rec * r, const char * pam_service,
	const char * login, const char * password, int steps) {
	pam_handle_t * pamh = NULL;
	struct pam_conv pam_conversation = { &pam_authenticate_conv, (void *) password };
	const char * stage = "PAM transaction failed for service";
	const char * param = pam_service;
	int ret;
	if ((ret = pam_start(pam_service, login, &pam_conversation, &pamh)) == PAM_SUCCESS) {
		if (steps & _PAM_STEP_AUTH) {
			param = login;
			stage = "PAM authentication failed for user";
			ret = pam_authenticate(pamh, PAM_SILENT | PAM_DISALLOW_NULL_AUTHTOK);
		}
		if ((ret == PAM_SUCCESS) && (steps & _PAM_STEP_ACCOUNT)) {
			param = login;
			stage = "PAM account validation failed for user";
			ret = pam_acct_mgmt(pamh, PAM_SILENT | PAM_DISALLOW_NULL_AUTHTOK);
		}
	}
	if (ret != PAM_SUCCESS) {
		const char * strerr = pam_strerror(pamh, ret);
		ap_log_error(APLOG_MARK, APLOG_WARNING, 0, r->server, "mod_authnz_pam: %s %s: %s", stage, param, strerr);
		apr_table_setn(r->subprocess_env, _EXTERNAL_AUTH_ERROR_ENV_NAME, apr_pstrdup(r->pool, strerr));
		pam_end(pamh, ret);
		return AUTH_DENIED;
	}
	apr_table_setn(r->subprocess_env, _REMOTE_USER_ENV_NAME, login);
	r->user = apr_pstrdup(r->pool, login);
	ap_log_error(APLOG_MARK, APLOG_NOTICE, 0, r->server, "mod_authnz_pam: PAM authentication passed for user %s", login);
	pam_end(pamh, ret);
	return AUTH_GRANTED;
}

APR_DECLARE_OPTIONAL_FN(authn_status, pam_authenticate_with_login_password,
	(request_rec * r, const char * pam_service,
	const char * login, const char * password, int steps));

module AP_MODULE_DECLARE_DATA authnz_pam_module;

static authn_status pam_auth_account(request_rec * r, const char * login, const char * password) {
	authnz_pam_config_rec * conf = ap_get_module_config(r->per_dir_config, &authnz_pam_module);

	if (!conf->pam_service) {
		return AUTH_GENERAL_ERROR;
	}

	return pam_authenticate_with_login_password(r, conf->pam_service, login, password, _PAM_STEP_ALL);
}

static const authn_provider authn_pam_provider = {
	&pam_auth_account,
};

#ifdef AUTHN_PROVIDER_VERSION
static authz_status check_user_access(request_rec * r, const char * require_args, const void * parsed_require_args) {
	if (!r->user) {
		return AUTHZ_DENIED_NO_USER;
	}

	const char * pam_service = ap_getword_conf(r->pool, &require_args);
	if (pam_service && pam_service[0]) {
		authn_status ret = pam_authenticate_with_login_password(r, pam_service, r->user, NULL, _PAM_STEP_ACCOUNT);
		if (ret == AUTH_GRANTED) {
			return AUTHZ_GRANTED;
		}
	}
	return AUTHZ_DENIED;
}
static const authz_provider authz_pam_provider = {
	&check_user_access,
        NULL,
};
#else
static int check_user_access(request_rec * r) {
	int m = r->method_number;
	const apr_array_header_t * reqs_arr = ap_requires(r);
	if (! reqs_arr) {
		return DECLINED;
	}
	require_line * reqs = (require_line *)reqs_arr->elts;
	int x;
	for (x = 0; x < reqs_arr->nelts; x++) {
		if (!(reqs[x].method_mask & (AP_METHOD_BIT << m))) {
			continue;
		}
		const char * t = reqs[x].requirement;
		const char * w = ap_getword_white(r->pool, &t);
		if (!strcasecmp(w, "pam-account")) {
			const char * pam_service = ap_getword_conf(r->pool, &t);
			if (pam_service && strlen(pam_service)) {
				authn_status ret = pam_authenticate_with_login_password(r, pam_service, r->user, NULL, _PAM_STEP_ACCOUNT);
				if (ret == AUTH_GRANTED) {
					return OK;
				}
			}
		}
	}
	return DECLINED;
}
#endif

static void register_hooks(apr_pool_t * p) {
#ifdef AUTHN_PROVIDER_VERSION
	ap_register_auth_provider(p, AUTHN_PROVIDER_GROUP, "PAM", AUTHN_PROVIDER_VERSION, &authn_pam_provider, AP_AUTH_INTERNAL_PER_CONF);
	ap_register_auth_provider(p, AUTHZ_PROVIDER_GROUP, "pam-account", AUTHZ_PROVIDER_VERSION, &authz_pam_provider, AP_AUTH_INTERNAL_PER_CONF);
#else
	ap_register_provider(p, AUTHN_PROVIDER_GROUP, "PAM", "0", &authn_pam_provider);
	ap_hook_auth_checker(check_user_access, NULL, NULL, APR_HOOK_MIDDLE);
#endif
	APR_REGISTER_OPTIONAL_FN(pam_authenticate_with_login_password);
}

module AP_MODULE_DECLARE_DATA authnz_pam_module = {
	STANDARD20_MODULE_STUFF,
	create_dir_conf,	/* Per-directory configuration handler */
	NULL,			/* Merge handler for per-directory configurations */
	NULL,			/* Per-server configuration handler */
	NULL,			/* Merge handler for per-server configurations */
	authnz_pam_cmds,	/* Any directives we may have for httpd */
	register_hooks		/* Our hook registering function */
};

