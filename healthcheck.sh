#!/bin/bash
echo "Check Services"
http=http://localhost:8080/nifi
status=`curl $http -k -s -f -o /dev/null && echo "UP" || echo "DOWN"`    
echo "Nifi Status: $status"
http=http://localhost:4571/_cat/health
status=`curl $http -k -s -f -o /dev/null && echo "UP" || echo "DOWN"`    
echo "Elasticsearch Status: $status"
http=http://localhost:5601
status=`curl $http -k -s -f -o /dev/null && echo "UP" || echo "DOWN"`    
echo "Kibana Status: $status"