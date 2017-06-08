#!/bin/sh

# Make sure solr is started
$SOLR_ROOT/bin/solr start -p 8983

# Uncomment to drop collection
# $SOLR_ROOT/bin/solr delete -c shortstories

# Create core and import schema
$SOLR_ROOT/bin/solr create -c shortstories
curl -X POST -H 'Content-type:application/json' --data-binary @schema.json http://localhost:8983/solr/shortstories/schema

# Restart solr
# See: https://stackoverflow.com/questions/29445323/adding-a-document-to-the-index-in-solr-document-contains-at-least-one-immense-t#31720634
$SOLR_ROOT/bin/solr stop -p 8983
$SOLR_ROOT/bin/solr start -p 8983
