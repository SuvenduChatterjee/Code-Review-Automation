
var modal = document.getElementById('id01');
var rules = document.getElementById("selected_rules");
var isSaved = document.getElementById('save_button');
var message = document.getElementById('rules_message');

// When the user clicks anywhere outside of the modal, do not close it
window.onclick = function(event) {
    if (event.target == modal) {
        //modal.style.display = "none";
    }
}

function doSomething(element){
    var isChecked=element;
  if(isChecked.checked == true)
  {
    document.getElementById('id01').style.display="block";
    isChecked.value="True";
    isSavedRules();
    
  }
  else{
    document.getElementById("001").style.visibility = "none";
  }
}

function modify_rules(element){
  if(element.checked == true){
    if(rules.value == ""){
      rules.value=element.value;
    }else{
      rules.value=rules.value +","+ element.value;
    }
  }else{
    if(rules.value.split(",").length == 1){
      rules.value=rules.value.replace(element.value,"");
    }else if(rules.value.split(",")[0] == element.value){
      rules.value=rules.value.replace(element.value+",","");
    }
    else{
      rules.value=rules.value.replace(","+element.value,"");
    }
  }
  //window.alert(rules.value);  //Left for future debuging
}

function isSavedRules(){
  var arrayOfRules = rules.value.split(",");
  var i;
  if(isSaved.value == "True"){
    for (i = 0; i < arrayOfRules.length; i++) {
      document.getElementById(arrayOfRules[i]).checked=true;
    }
  }else{
    for (i = 0; i < arrayOfRules.length; i++) {
      document.getElementById(arrayOfRules[i]).checked=false;
    }
    rules.value="";
  }
  
}

function save(flag){
  if(flag){
    isSaved.value="True";
    applyMessage('Rules selection is applicable',true);
  }
  else{
    isSaved.value="False";
    applyMessage('Default rules in effect',false);
  }
}

function applyMessage(tmessage,displayCount){
  if (displayCount){
    var arrayOfRules = rules.value.split(",");
    var count= arrayOfRules.length
    if(rules.value.length==0){
      message.innerHTML=tmessage+" no rule in effect";
      message.style.color='red'
    }else if(count==1){
      message.innerHTML=tmessage+" "+count+" rule in effect";
      message.style.color='green'
    }else{
      message.innerHTML=tmessage+" "+count+" rules in effect";
      message.style.color='green'
    }
  }
  else{
    message.innerHTML=tmessage;
    message.style.color='blue'
  }
}

//File upload display
function chengeName(){
  var fileName = document.getElementById('validatedCustomFile').value.split("\\")[2];
  if(fileName){
    document.getElementById('file_name').innerHTML=fileName;
  }
  else{
    document.getElementById('file_name').innerHTML="Upload Content Pack...";
  }
}