// JavaScript Document
var still_loading = false

function get_friends(){
    friends_xmlHttp=GetXmlHttpObject()
    if (friends_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX£¡");
	   	return;
    }
    still_loading = true;
	var url="/"+m_origin+"friends?sid="+Math.random()+"&nextslice=true";
	friends_xmlHttp.onreadystatechange=getfriends_stateChanged;
	friends_xmlHttp.open("GET",url,true);
	friends_xmlHttp.send(null);
	
	document.getElementById('loading').style.display = 'block';
}

function getfriends_stateChanged() 
{ 
  if (friends_xmlHttp.readyState==4)
  {
  	 if(friends_xmlHttp.responseText != "done"){
	 	 document.getElementById("friends_table").innerHTML += friends_xmlHttp.responseText;
	 }
	 else
	 	done = true;
 	 still_loading = false;
 	 document.getElementById('loading').style.display = 'none';
  }
}

function load_more_friends()
{
    if(m_origin!="" && !done && !still_loading){
        
        var t = document.body.scrollTop | document.documentElement.scrollTop;
        var h = get_smaller(document.body.scrollHeight, document.documentElement.scrollHeight);
        var window_height = get_smaller(document.body.clientHeight, document.documentElement.clientHeight);
//        alert('scrollTop:'+t+'\nscrollHeight:'+h+'\nwindowheight:'+window_height);
        if(t + window_height > h-100){
            //alert('scrollTop:'+t+'\nscrollHeight:'+h+'\nwindowheight:'+window_height);
            get_friends();
        }
    }    
}
function get_smaller(a, b)
{
    if(a <= 0)
        a = 100000000;
    if(b <= 0)
        b = 100000000;
    return Math.min(a, b);
}
