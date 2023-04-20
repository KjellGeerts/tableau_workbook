#!/bin/sh -l

cd /

tabcmd login --server https://dub01.online.tableau.com --site biztorybenelux --token-name publish_token --token-value 
tabcmd publish "yelp_analyses.twb" -n "Yelp Analyses" -r "Sandbox" --db-username "" --db-password "" --save-db-password -o
tabcmd logout
