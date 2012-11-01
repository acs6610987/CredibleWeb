var selected_item = null

function search_placeholder(tag, m_focus)
{
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
function expand_collapsed(m_content)
{
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

function get_news(tag)
{
    change_focus(tag);
    document.getElementById('content').innerHTML = "<ul id='content_news'></ul>";
    news_xmlHttp=GetXmlHttpObject()
    if (news_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX£¡");
	   	return;
    }
	var url="/?sid="+Math.random()+"&firstload=true";
	news_xmlHttp.onreadystatechange=getnews_stateChanged;
	news_xmlHttp.open("GET",url,true);
	news_xmlHttp.send(null);
}

function getnews_stateChanged()
{
    if (news_xmlHttp.readyState==4)
    {
//        alert(xmlHttp.responseText)
        document.getElementById("content_news").innerHTML += news_xmlHttp.responseText;
        document.getElementById('loading').style.display = 'none';
    }	 
}

function get_evaluation(tag)
{
    change_focus(tag);
    document.getElementById('content').innerHTML = "";
    eval_xmlHttp=GetXmlHttpObject()
    if (eval_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX£¡");
	   	return;
    }
	var url="/geteval?sid="+Math.random();
	eval_xmlHttp.onreadystatechange=getevaluation_stateChanged;
	eval_xmlHttp.open("GET",url,true);
	eval_xmlHttp.send(null);
}

function getevaluation_stateChanged()
{
    if (eval_xmlHttp.readyState==4)
    {
//        alert(xmlHttp.responseText)
        document.getElementById("content").innerHTML = eval_xmlHttp.responseText;
        document.getElementById('loading').style.display = 'none';
    }
}

function get_myratings(tag){
    change_focus(tag);
    document.getElementById('content').innerHTML = "<ul id='content_ratings'></ul>";
    ratings_xmlHttp=GetXmlHttpObject()
    if (ratings_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX!");
	   	return;
    }
	var url="/getratings?sid="+Math.random();
	ratings_xmlHttp.onreadystatechange=getratings_stateChanged;
	ratings_xmlHttp.open("GET",url,true);
	ratings_xmlHttp.send(null);
}
function getratings_stateChanged(){
    if (ratings_xmlHttp.readyState==4)
    {
//        alert(xmlHttp.responseText)
        document.getElementById("content_ratings").innerHTML += ratings_xmlHttp.responseText;
        document.getElementById('loading').style.display = 'none';
    }	
}

function merge_account(tag, suburl){
    change_focus(tag);
    document.getElementById('content').innerHTML = "";
    merge_xmlHttp=GetXmlHttpObject()
    if (merge_xmlHttp==null)
    {
   	    alert ("Your browser doesn't support AJAX!");
	   	return;
    }
	var url="/" + suburl + "?sid="+Math.random();
	merge_xmlHttp.onreadystatechange=merge_stateChanged;
	merge_xmlHttp.open("GET",url,true);
	merge_xmlHttp.send(null);
	
	document.getElementById('loading').style.display = 'block';
}
function merge_stateChanged(){
    if (merge_xmlHttp.readyState==4)
    {
        
        document.getElementById("content").innerHTML = merge_xmlHttp.responseText;
        document.getElementById('loading').style.display = 'none';
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
    hint.innerHTML="<ul id='hint_list'></ul>";
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
        document.getElementById("hint_list").innerHTML = showHint_xmlHttp.responseText;
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
    fu_xmlHttp=GetXmlHttpObject()
  
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
