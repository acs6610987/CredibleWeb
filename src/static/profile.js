// JavaScript Document
function check_profile(m_form){
    if(m_form.realname.value == ""){
        document.getElementById('profile_info').innerHTML = "Realname can't be empty.";
        return false;
    }
    return true;
}
