// JavaScript Document
current_url = null
function check_eval_form(m_form)
{
    if(m_form.rating.value)
        return true;
    return false;
}
//function submit_rating(m_form, url){
//    var i = 0;
//    for(i = 0; i < m_form.rating.length; i++)
//        if(m_form.rating[i].checked)
//            break;
//    sr_xmlHttp = GetXmlHttpObject();
//    if(sr_xmlHttp == null){
//        alert ("Your browser doesn't support AJAX!");
//	   	return;
//    }
//    current_url = url
//    var request ="/evaluate?sid="+Math.random();
//	sr_xmlHttp.onreadystatechange=submitRating_stateChanged;
//	sr_xmlHttp.open("POST",request,true);
//	sr_xmlHttp.setRequestHeader("content-type", "application/x-www-form-urlencoded;");
//	var str = 'url='+encodeURIComponent(url)+'&rating='+m_form.rating[i].value;
//	sr_xmlHttp.send(str);
//}
//function submitRating_stateChanged(){
//    if(sr_xmlHttp.readyState == 4){
////        document.getElementById('evalmessage').innerHTML = 'You have rated this page.';
//        document.getElementById('cheer_dialog').style.display = 'block';
//        show_status(current_url)
//    }
//}

function submit_rating(m_form_id, url, points){
    var m_form = document.getElementById(m_form_id);
    var comment = encodeURIComponent(m_form.comment.value);
    var overall_rating = m_form.overall_rating.value;
    var truthfullesss = m_form.truthfulness.value;
    var unbiased = m_form.unbiased.value;
    var security = m_form.security.value;
    var design = m_form.design.value;
    if(comment == ""){
        document.getElementById('help_block').innerHTML = "<div class=\"alert alert-error\">" +
            "<button type='button' class='close' data-dismiss='alert'>×</button>"+
            "Try to say something in your review."+
            "</div>";
        return;
    }
    ssr_xmlHttp = GetXmlHttpObject();
    if(ssr_xmlHttp == null){
        alert ("Your browser doesn't support AJAX!");
	   	return;
    }
    current_url = url
    var request ="/evaluate?sid="+Math.random();
	ssr_xmlHttp.onreadystatechange=function(){
	   if(ssr_xmlHttp.readyState == 4){
//           document.getElementById('my_eval').style.display = 'none';
           //increase user points on bottom bar
           document.getElementById('eval-tab1').innerHTML = ssr_xmlHttp.responseText;
           user_points = parseInt(document.getElementById('user_points').innerHTML, 10);
           user_points += points;
           document.getElementById('user_points').innerHTML = user_points;

           show_points_gaining(points);
           load_comments(url);
           load_status(url);
        }
    };
	ssr_xmlHttp.open("POST",request,true);
	ssr_xmlHttp.setRequestHeader("content-type", "application/x-www-form-urlencoded;");
	var str = 'url='+encodeURIComponent(url)+'&points='+points+
            '&overall_rating='+ overall_rating +
            '&comment=' + comment +
            '&truthfulness='+ truthfullesss +
            '&unbiased=' + unbiased +
            '&security=' + security +
            '&design=' + design;
	ssr_xmlHttp.send(str);
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

function evalScore(m_root, m_event, m_input_id){
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
    if(m_input_id != ''){
        var targetObj =  document.getElementById(m_input_id);
        targetObj.value = clickedImgId[clickedImgId.length-1];
    }
//    var attitudeTitle = document.getElementById(m_title_id);
//    attitudeTitle.innerHTML = eventTarget.title;
}
function evalChoice(m_root, img_id_beginning, m_input_id)
{
    var imgs = m_root.getElementsByTagName("img");
    m_input = document.getElementById(m_input_id);
    clickedImgId = img_id_beginning + m_input.value;
    for(var i=0; i<imgs.length; i++) {
        var tempImg = imgs[i];
        if(tempImg.id <= clickedImgId){
            tempImg.src ='/static/star.png';
        }
        else {
            tempImg.src ='/static/star-bw.png';
        }
    }
//    clickedImg = document.getElementById(clickedImgId);
//    var attitudeTitle = document.getElementById(m_title_id);
//    attitudeTitle.innerHTML = clickedImg.title;
}

function show_eval_block(url){
    var m_root = document.getElementById('my_eval_stars');
    var imgs = m_root.getElementsByTagName("img");
    var m_input1 = document.getElementById('eval_simple_rating'), m_input2 = document.getElementById('my_eval_score');
    m_input2.value = m_input1.value;
    clickedImgId = 'fstar' + m_input2.value;
    for(var i=0; i<imgs.length; i++) {
        var tempImg = imgs[i];
        if(tempImg.id <= clickedImgId){
            tempImg.src ='/static/star.png';
        }
        else {
            tempImg.src ='/static/star-bw.png';
        }
    }
    document.getElementById('eval_container').style.display = 'block';
    load_comments(url);
    load_status(url);
}
function load_reviews(url)
{
    load_comments(url);
    load_status(url);
}
function load_comments(url)
{
    lc_xmlHttp = GetXmlHttpObject();
    if(lc_xmlHttp == null){
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    lc_xmlHttp.onreadystatechange=function(){
        if(lc_xmlHttp.readyState == 4){
            document.getElementById('eval_comments').innerHTML = lc_xmlHttp.responseText;
        }
    };
    var request ="/getratings_url?sid="+Math.random()+'&url='+encodeURIComponent(url);
    lc_xmlHttp.open("GET",request,true);
    lc_xmlHttp.send(null);
}

function load_status(url){
    ls_xmlHttp = GetXmlHttpObject();
    if(ls_xmlHttp == null){
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    ls_xmlHttp.onreadystatechange = function(){
        if(ls_xmlHttp.readyState == 4){
            document.getElementById('eval_stat').innerHTML = ls_xmlHttp.responseText;
        }
    }
    var request = "/getratings_status?sid="+Math.random()+'&url='+encodeURIComponent(url);
    ls_xmlHttp.open("GET", request, true);
    ls_xmlHttp.send(null);
}

function show_points_gaining(points){
    pointsObj = document.getElementById('gain_points');
    pointsObj.innerHTML = "+ "+points+" Points";
    pointsObj.style.display = "block";
    var bottom = 50,  opacity = 1;
    var setp = setInterval(function(){
        opacity -= 0.01;
        bottom += 3;
        pointsObj.style.opacity = opacity;
        pointsObj.style.bottom = bottom + "px";
        if(opacity <= 0){
            clearInterval(setp);
            pointsObj.style.display = "none";
        }
    }, 40)
}

function upvote(rid){
    vote_xmlHttp = GetXmlHttpObject();
    if(vote_xmlHttp == null){
        alert ("Your browser doesn't support AJAX!");
        return;
    }
    vote_xmlHttp.onreadystatechange = function(){
        if(vote_xmlHttp.readyState == 4){
            var status = vote_xmlHttp.responseText;
            var message = document.getElementById('vote_message');
            var votes = parseInt(document.getElementById('vote_number').innerHTML, 10);
            if(status == '0')
                message.innerHTML = 'Thanks, you have already voted this review.';
            else{
                message.innerHTML = 'Well done! Your vote will help others.';
                votes += 1;
            }
            document.getElementById('vote_number').innerHTML = votes;
        }
    }
    var request = "/vote?sid="+Math.random()+'&rid='+encodeURIComponent(rid);
    vote_xmlHttp.open("GET", request, true);
    vote_xmlHttp.send(null);
}