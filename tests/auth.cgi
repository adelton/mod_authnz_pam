#!/bin/bash

echo "Content-Type: text/plain"
echo "Pragma: no-cache"
echo
if [ -n "$REMOTE_USER" ] ; then
	echo "User $REMOTE_USER."
else
	echo "Not authenticated."
fi
