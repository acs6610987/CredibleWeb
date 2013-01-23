// JavaScript Document
function check_reg_info(m_form)
{
    firstname = m_form.firstname.value;
    lastname = m_form.lastname.value;
//    username = m_form.username.value;
    password = m_form.password.value;
    cf_password = m_form.confirm_password.value;
    email = m_form.email.value;
    
    if(firstname == '' || lastname == '' || password == '' || cf_password == '' || email == '')
    {
        document.getElementById('help_block').innerHTML = "<div class=\"alert alert-error\">" +
            "<button type='button' class='close' data-dismiss='alert'>×</button>"+
            "You have to fill in the required(*) fields."+
            "</div>";
        return false;
    }
    if(password != cf_password)
    {
        document.getElementById('help_block').innerHTML = "<div class=\"alert alert-error\">" +
            "<button type='button' class='close' data-dismiss='alert'>×</button>"+
            "Two passwords don't match."+
            "</div>";
        return false;
    }
    expertise = m_form.expertise;
    for(i = 0; i < expertise.length; i++)
        if(expertise[i].checked)
            return true;
    document.getElementById('help_block').innerHTML = "<div class=\"alert alert-error\">" +
        "<button type='button' class='close' data-dismiss='alert'>×</button>"+
        "You need to choose at least one expertise(or interest)."+
        "</div>";
    return false;
}

function check_email(email)
{
    xmlHttp=GetXmlHttpObject()
    if (xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX!");
	   	return;
    }
	var url="/register?sid="+Math.random()+"&email="+ encodeURIComponent(email);
	xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState == 4){
            if(xmlHttp.responseText == 'exist')
                document.getElementById('email_info').innerHTML = "<span class='text-error'>"+
                    "This email address has been used.</span>";
            else
                document.getElementById('email_info').innerHTML = "<span class='text-success'>"+
                     "This email address looks good.</span>";
        }
    };
	xmlHttp.open("GET",url,true);
	xmlHttp.send(null);
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
