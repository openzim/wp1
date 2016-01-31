#!/opt/ts/bin/bash
HOME=/home/project/e/n/w/enwp10
export HOME

echo -e "Content-type: text/html\n\n";

echo "<html><body>"

echo "<h1>Projects with Importance=NotAClass pages</h1>"

echo "select p_project, p_icount, count(r_article) as NotAClass from projects join ratings on p_project = r_project where p_icount > 0 and (r_importance = 'NotA-Class') group by p_project order by NotAClass asc/* SLOW_OK */;" \
   | /opt/ts/mysql/5.1/bin/mysql -h sql-s1 p_enwp10 -H

echo "</body></html>"

echo "<h1>Projects with Quality=NotAClass pages</h1>"

echo "select p_project, count(r_article) as NotAClass from projects join ratings on p_project= r_project where r_quality = 'NotA-Class' group by p_project order by NotAClass asc /* SLOW_OK */;" \
   | /opt/ts/mysql/5.1/bin/mysql -h sql-s1 p_enwp10 -H
