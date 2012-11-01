// JavaScript Document
function show_status(url){
    if(url.substr(0,4) != 'http'){
        url = 'http://' + url;
    }
    status_xmlHttp=GetXmlHttpObject()
    if (status_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX£¡");
	   	return;
    }
	var url="/geteval_status?sid="+Math.random()+'&url='+ encodeURIComponent(url);
	status_xmlHttp.onreadystatechange=getStatus_stateChanged;
	status_xmlHttp.open("GET",url,true);
	status_xmlHttp.send(null);
}

function getStatus_stateChanged()
{
    if (status_xmlHttp.readyState==4)
    {
        document.getElementById('status_table').innerHTML = status_xmlHttp.responseText;
       // document.getElementById('loading').style.display = 'none';
    }
}
