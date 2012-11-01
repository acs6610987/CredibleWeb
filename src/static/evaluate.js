// JavaScript Document
current_url = none
function check_eval_form(m_form)
{
    if(m_form.rating.value)
        return true;
    return false;
}
function submit_rating(m_form, url){
    var i = 0;
    for(i = 0; i < m_form.rating.length; i++)
        if(m_form.rating[i].checked)
            break;
    sr_xmlHttp = GetXmlHttpObject();
    if(sr_xmlHttp == null){
        alert ("Your browser doesn't support AJAX!");
	   	return;
    }
    current_url = url
    var request ="/evaluate?sid="+Math.random();
	sr_xmlHttp.onreadystatechange=submitRating_stateChanged;
	sr_xmlHttp.open("POST",request,true);
	sr_xmlHttp.setRequestHeader("content-type", "application/x-www-form-urlencoded;");
	var str = 'url='+encodeURIComponent(url)+'&rating='+m_form.rating[i].value;
	sr_xmlHttp.send(str);
}
function submitRating_stateChanged(){
    if(sr_xmlHttp.readyState == 4){
//        document.getElementById('evalmessage').innerHTML = 'You have rated this page.';
        document.getElementById('cheer_dialog').style.display = 'block';
        show_status(current_url)
    }
}

function submit_simplerating(m_form, url){
    ssr_xmlHttp = GetXmlHttpObject();
    if(ssr_xmlHttp == null){
        alert ("Your browser doesn't support AJAX!");
	   	return;
    }
    current_url = url
    var request ="/evaluate?sid="+Math.random();
	ssr_xmlHttp.onreadystatechange=submitSimpleRating_stateChanged;
	ssr_xmlHttp.open("POST",request,true);
	ssr_xmlHttp.setRequestHeader("content-type", "application/x-www-form-urlencoded;");
	var str = 'url='+encodeURIComponent(url)+'&rating='+m_form.rating.value;
	ssr_xmlHttp.send(str);
}
function submitSimpleRating_stateChanged(){
    if(ssr_xmlHttp.readyState == 4){
        document.getElementById('cheer_dialog').style.display = 'block';
        show_status(current_url)
    }
}

function over_close(tag, flag){
    if(flag){
        tag.style.backgroundColor = '#dddddd';
        tag.style.cursor = 'pointer';
    }
    else{
        tag.style.backgroundColor = 'white';
        tag.style.cursor = 'default';
    }
}

function display_stat(url){
    var status_table = document.getElementById('status_table')
    if(status_table.style.display == 'none' || status_table.style.display == ''){
        show_status(url);
        status_table.style.display = 'block';
    }
    else
        status_table.style.display = 'none';
}

function evalScore(m_root, m_event, m_id, m_title_id){
    var imgs = m_root.getElementsByTagName("img");
    if(!m_event)
        m_event = window.event;
    var eventTarget = m_event.srcElement|| m_event.target || eventTag.target;
    if(eventTarget.tagName.toUpperCase() != 'IMG')
        return;
    var clickedImgId = eventTarget.id;
    for(var i=0; i<imgs.length; i++) {
        var tempImg = imgs[i];
        if(tempImg.id <= clickedImgId){
            tempImg.src ='/static/star.png';
        }
        else {
            tempImg.src ='/static/star-bw.png';
        }
    }
    var targetObj =  document.getElementById(m_id);
    targetObj.value = clickedImgId[clickedImgId.length-1];
    var attitudeTitle = document.getElementById(m_title_id);
    attitudeTitle.innerHTML = eventTarget.title;
}
