tabcmd login --server https://dub01.online.tableau.com --site biztorybenelux --token-name publish_token --token-value ptUMOuxeQmigIPIH0hkW4A==:Fw2QQXtcuyFmsOVnjnqGBA0gOWhDNPJ2
tabcmd publish "yelp_analyses.twb" -n "Yelp Analyses" -r "Sandbox" --db-username "TABLEAU_USER" --db-password "Kjell.01" --save-db-password -o
tabcmd logout
