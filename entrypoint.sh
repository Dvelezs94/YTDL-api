#!/bin/sh

echo "Args: $@"
# init supervisor or sidekiq
case "$1" in
  api)
    /usr/bin/supervisord -c /etc/supervisord.conf
  ;;
  ## use this like bash .entrypoint.sh echo "hello". you can give it any number of arguments after run
  *)
    shift
    echo "running: $@"
    $@
  ;;
esac