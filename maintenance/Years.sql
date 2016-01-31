select pl_title
  from pagelinks join page as src on pl_from = src.page_id
  join page as dst on pl_namespace = dst.page_namespace
              and pl_title = dst.page_title
 where src.page_namespace = 0 
   and src.page_title = 'List_of_years'
   and dst.page_namespace = 0;

