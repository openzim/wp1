function projectSelected () { 
  var sel = document.getElementById("projectsel");
  var name = document.getElementById("projectname");
  name.value = sel.options[sel.selectedIndex].value;
}
