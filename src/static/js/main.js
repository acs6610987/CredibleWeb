var selected_item = null
window.onload = check_message
//document.onclick = hide_block

//function hide_block(e){
//    if (!e) 
//        var e = window.event;
//    if (e.target) 
//        targ = e.target;
//    else if (e.srcElement) 
//        targ = e.srcElement;
//    src_id = targ.getAttribute('id');
//    if(src_id != 'topnav-hint' && src_id != 'topnav-hint-input')
//        document.getElementById('topnav-hint').style.display = 'none';
//    if(src_id != 'friendreq_box' && src_id != 'friendreq_box_img')
//        document.getElementById('friendreq_box').style.display = 'none';
//}

function check_message(){
    checkm_xmlHttp = GetXmlHttpObject();
    if (checkm_xmlHttp==null)
    {
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    var url="/checkfriendrequest?sid="+Math.random();
	checkm_xmlHttp.onreadystatechange=function(){
	   if(checkm_xmlHttp.readyState == 4){
            document.getElementById('friendreq_box').innerHTML = checkm_xmlHttp.responseText;
	   }
    };
	checkm_xmlHttp.open("GET",url,true);
	checkm_xmlHttp.send(null);
}
function agree_request(uid, m_parent){
    agreereq_xmlHttp = GetXmlHttpObject();
    if (agreereq_xmlHttp==null)
    {
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    var url="/agreefriendrequest?sid="+Math.random()+"&uid="+uid;
	agreereq_xmlHttp.onreadystatechange=function(){
	   if(agreereq_xmlHttp.readyState == 4){
	       if(agreereq_xmlHttp.status == 200){
	           m_parent.innerHTML = "<input type='button' value='Friend' readonly='readonly' class='noneditable' />";
	       }
	   }
    };
	agreereq_xmlHttp.open("GET",url,true);
	agreereq_xmlHttp.send(null);
}

function ignore_request(uid, m_parent){
    ignorereq_xmlHttp = GetXmlHttpObject();
    if (ignorereq_xmlHttp==null)
    {
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    var url="/ignorefriendrequest?sid="+Math.random()+"&uid="+uid;
	ignorereq_xmlHttp.onreadystatechange=function(){
	   if(ignorereq_xmlHttp.readyState == 4){
	       if(ignorereq_xmlHttp.status == 200){
	           m_parent.innerHTML = "<input type='button' value='Ignored' readonly='readonly' class='noneditable' />";
	       }
	   }
    };
	ignorereq_xmlHttp.open("GET",url,true);
	ignorereq_xmlHttp.send(null);
}

function search_placeholder(tag, m_focus, hint_blockid)
{
    m_block = document.getElementById(hint_blockid);
    if(m_focus){
        if(tag.value == "search for user")
            tag.value = "";
        tag.style.color = 'black';
    }
    else{
        if(tag.value == "")
            tag.value = "search for user";
        tag.style.color = 'grey';
    }
}

function over_content(src, flag){
    if(src == selected_item)
        return;
	if(flag == true){
		src.style.cursor = 'pointer';
		src.style.backgroundColor = '#eeeeee';
	}
	else{
		src.style.cursor = 'default';
		src.style.backgroundColor = '#f9f9f9';
	}
}
function expand_collapsed()
{
    if(arguments.length == 1)
        m_content = document.getElementById(arguments[0]);
    else if(arguments.length == 2)
        m_content = (arguments[1].getElementsByClassName(arguments[0]))[0];
    if(m_content.style.display == "none" || m_content.style.display == '')
        m_content.style.display = "block";
    else
        m_content.style.display = "none";
}
function change_focus(tag)
{
    if(tag == undefined || tag == null)
        return;
    if(selected_item != null)
        selected_item.style.backgroundColor = '';
    selected_item = tag;
    selected_item.style.backgroundColor = '#dddddd';
}

function load_more_news()
{
    morenews_xmlHttp=GetXmlHttpObject()
    if (morenews_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX��");
	   	return;
    }
	var url="/morenews?sid="+Math.random();
	morenews_xmlHttp.onreadystatechange=function(){
        if(morenews_xmlHttp.readyState == 4){
            text = morenews_xmlHttp.responseText;
            if(text == ''){
                document.getElementById('see_more_news').style.display = 'none';
            }
            else{
                document.getElementById('content_news').innerHTML += text;
            }
            document.getElementById('loading').style.display = 'none';
        }
    };
	morenews_xmlHttp.open("GET",url,true);
	morenews_xmlHttp.send(null);
    document.getElementById('loading').style.display = 'block';
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

function open_page(url)
{
    if(url.substr(0,4) != 'http'){
        url = 'http://' + url;
    }
    window.open('/evaluate?url='+ encodeURIComponent(url), 'evaluate_window');
}

function showHint(keyword){
    hint = document.getElementById("topnav-hint");
    if (keyword.length==0)
    { 
        hint.innerHTML="";
        hint.style.display = 'none';
        return;
    }
    hint.style.display = 'block';
    showHint_xmlHttp=GetXmlHttpObject()
  
    if (showHint_xmlHttp==null)
    {
        alert ("Your browser doesn't support AJAX!");
        return;
    }

    var url="/search?sid="+Math.random()+"&keyword="+encodeURIComponent(keyword)+"&hint=true";
	showHint_xmlHttp.onreadystatechange=showHint_stateChanged;
	showHint_xmlHttp.open("GET",url,true);
	showHint_xmlHttp.send(null);
}
function showHint_stateChanged(){
    if (showHint_xmlHttp.readyState==4)
    {
        if(showHint_xmlHttp.responseText == '')
            document.getElementById('topnav-hint').innerHTML = 'No user has been found.';
        else
            document.getElementById("topnav-hint").innerHTML = showHint_xmlHttp.responseText;
    }	
}
function follow_user(uid, tag){
    if(tag.value=="Cancel Following"){
        follow = false;
        tag.value = "Follow";
    }
    else{
        follow = true;
        tag.value = "Cancel Following";
    }
    fu_xmlHttp=GetXmlHttpObject();
  
    if (fu_xmlHttp==null)
    {
        alert ("Your browser doesn't support AJAX!");
        return;
    }

    var url="/followuser?sid="+Math.random()+"&uid="+uid+"&follow="+follow;
	fu_xmlHttp.onreadystatechange=followUser_stateChanged;
	fu_xmlHttp.open("GET",url,true);
	fu_xmlHttp.send(null);
}
function followUser_stateChanged(){
    if(fu_xmlHttp.readyState==4){
        
    }
}
function add_friend(uid, tag){
    var p = tag.parentNode;
    p.innerHTML = "<button type='button' class='btn btn-info' disabled>Request Sent</button>";
//    tag.value = "Request Sent";
//    tag.className = "noneditable";
//    tag.readOnly = "readonly";
    
    af_xmlHttp = GetXmlHttpObject();
    if (af_xmlHttp==null)
    {
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    var url="/addfriendrequest?sid="+Math.random()+"&uid="+uid;
	af_xmlHttp.onreadystatechange=function(){
    };
	af_xmlHttp.open("GET",url,true);
	af_xmlHttp.send(null);
}
