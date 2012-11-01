// JavaScript Document
function check_reg_info(m_form)
{
    realname = m_form.realname.value;
    username = m_form.username.value;
    password = m_form.password.value;
    cf_password = m_form.confirm_password.value;
    
    if(realname == '' || username=='' || password == '' || cf_password == '')
    {
        document.getElementById('reg_tip').innerHTML = "Empty info is not accepted!";
        return false;
    }
    if(password != cf_password)
    {
        document.getElementById('reg_tip').innerHTML = "Two passwords don't match.";
        return false;
    }
    return true;
}

function check_username(username)
{
    xmlHttp=GetXmlHttpObject()
    if (xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX!");
	   	return;
    }
	var url="/register?sid="+Math.random()+"&username="+ encodeURIComponent(username);
	xmlHttp.onreadystatechange=check_stateChanged;
	xmlHttp.open("GET",url,true);
	xmlHttp.send(null);
}

function check_stateChanged(){
    if(xmlHttp.readyState == 4){
        if(xmlHttp.responseText == 'exist')
            document.getElementById('reg_tip').innerHTML = "This username has been taken! Please Try another one.";
        else
            document.getElementById('reg_tip').innerHTML = "";
    }
}

function GetXmlHttpObject()
{
  var xmlHttp=null;
  try
    {
    // Firefox, Opera 8.0+, Safari
    xmlHttp=new XMLHttpRequest();
    }
  catch (e)
    {
    // Internet Explorer
    try
      {
      xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
      }
    catch (e)
      {
      xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
      }
    }
  return xmlHttp;
}

function check_feedback(m_form){
    if(m_form.description.value == ''){
        document.getElementById('feedback_tip').innerHTML = "Some required field has not been filled in.";
        document.getElementById('feedback_description').style.border = 'solid #cc0000';
        return false;
    }
    return true;
}
