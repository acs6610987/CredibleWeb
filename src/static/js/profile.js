// JavaScript Document
function check_profile(m_form){
    firstname = m_form.firstname.value;
    lastname = m_form.lastname.value;
    if(firstname == '' || lastname == '')
    {
        document.getElementById('help_block').innerHTML = "<div class=\"alert alert-error\">" +
            "<button type='button' class='close' data-dismiss='alert'>×</button>"+
            "You have to fill in the required(*) fields."+
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

function edit_request(){
    edit_xmlHttp=GetXmlHttpObject()
    if (edit_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX��");
	   	return;
    }
	var url="/edit_cwprofile?sid="+Math.random();
	edit_xmlHttp.onreadystatechange=function(){
	   if(edit_xmlHttp.readyState == 4)
	   {
	       block = document.getElementById('cw_editprofile_block');
	       block.style.display = 'block';
	       block.innerHTML = edit_xmlHttp.responseText;
	   }
    };
	edit_xmlHttp.open("GET",url,true);
	edit_xmlHttp.send(null);
}
