select dest.page_title from page as dest
 join pagelinks on pl_namespace = dest.page_namespace
                  and pl_title = dest.page_title
 join page as source on pl_from = source.page_title
 where source.page_namespace = 0 
   and source.page_title = 'List_of_decades'
   and dest.page_namespace = 0;

