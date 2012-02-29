require "luasql.postgres"

--[[

    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.not distributed

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is FeePyBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2011-2012 VoiceWARE Communications, Inc. All Rights Reserved.

    http://www.vwci.com/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.

]]--

digits = ""

env = assert(luasql.postgres())
con = assert(env:connect("dbname=pbx user=pbxuser password=secretpass1 host=127.0.0.1"))

function rows(sql)
    local cursor = assert (con:execute (sql))
    return function ()
        return cursor:fetch()
    end
end

function session_hangup_hook()
    freeswitch.consoleLog("NOTICE", "Session hangup\n")
    con:close()
end

function startswith(sbig, slittle)
    if type(slittle) == "table" then
        for k,v in ipairs(slittle) do
            if string.sub(sbig, 1, string.len(v)) == v then
                return true
            end
        end
        return false
    end
    return string.sub(sbig, 1, string.len(slittle)) == slittle
end

function key_press(session, input_type, data, args)
    if input_type == "dtmf" then
        digits = tostring(data['digit'])
        digits = digits .. session:getDigits(3, "", 2000, 3000)
        io.write("digit: [" .. data['digit'] .. "]\nduration: [" .. data['duration'] .. "]\n")
        freeswitch.consoleLog("info", "Key pressed: " .. data["digit"])
        return "break"
    else
        io.write(data:serialize("xml"))
        e = freeswitch.Event("message")
        e:add_body("you said " .. data:get_body())
        session:sendEvent(e)
    end
end

function log(logval)
    freeswitch.consoleLog("NOTICE", "----------------->" .. tostring(logval) .. "<------------- \n")
end

function blacklisted(num, context)
    db = assert(con:execute(string.format("SELECT * from pbx_blacklisted_numbers where context= '%s' and cid_number ='%s'", context, tostring(num))))
    if db:numrows() > 0 then
        return true
    else
        return false
    end
end

function get_cid_route(num, context)
    db = assert(con:execute(string.format("SELECT * from pbx_caller_id_routes where context= '%s' and cid_number ='%s'", context, tostring(num))))
    cid_route = db:fetch({}, "a")
    if db:numrows() > 0 then
        send_route(get_route_by_id(cid_route["pbx_route_id"]), context)
    else
        return false
    end
    return true
end

function get_route_by_did(did)
    db = assert(con:execute(string.format("SELECT pbx_routes.* from pbx_routes inner join pbx_dids on pbx_routes.id = pbx_dids.pbx_route_id where pbx_dids.did = '%s'", tostring(did))))
    return db:fetch({}, "a")
end

function get_route_by_id(id)
    db = assert(con:execute(string.format("SELECT * from pbx_routes where id = %d", tonumber(id))))
    return db:fetch({}, "a")
end

function get_cc(name, context)
    db = assert(con:execute(string.format("SELECT * from call_center_queues where name = '%s' and context = '%s'", name, context)))
    return db:fetch({}, "a")
end

function get_cc_position(name)
    db = assert(con:execute(string.format("SELECT count(*) as num from call_center_callers where queue = '%s'", name)))
    return db:fetch({}, "a")
end


function get_group(name, context)
    db = assert(con:execute(string.format("SELECT * from pbx_groups where name = '%s' and context = '%s'", name, context)))
    return db:fetch({}, "a")
end

function get_cc_tier_agents(name)
    db = assert(con:execute(string.format("SELECT count(*) as agent_num from call_center_tiers where queue = '%s'", name)))
    return db:fetch({}, "a")
end

function get_tts_by_id(name, context)
    db = assert(con:execute(string.format("SELECT * from pbx_tts where id = %d and context = '%s'", tonumber(name), context)))
    return db:fetch({}, "a")
end

function get_route_by_ext(ext,context)
    log(ext)
    db = assert(con:execute(string.format("select * from pbx_routes where name = '%s' and context = '%s'", tostring(ext), context)))
    return db:fetch({}, "a")
end

function get_route_by_ivr_opt(option, id)
    db = assert(con:execute(string.format("SELECT * from pbx_routes INNER JOIN pbx_ivr_options " ..
            "ON pbx_routes.id = pbx_ivr_options.pbx_route_id " ..
            "WHERE pbx_ivr_options.option ='%s' " ..
            "AND pbx_ivr_options.pbx_ivr_id=%d", option, tonumber(id))))
    return db:fetch({}, "a")
end

function get_virtual_extension(route, context)
    db = assert(con:execute(string.format("SELECT * from pbx_virtual_extensions where extension= '%s' and context ='%s'", route["name"], context)))
    return db:fetch({}, "a")
end

function get_virtual_mailbox(route, context)
    db = assert(con:execute(string.format("SELECT * from pbx_virtual_extensions where extension= '%s' and context ='%s'", route["name"], context)))
    return db:fetch({}, "a")
end

function get_default_gateway(context)
    db = assert(con:execute(string.format("select default_gateway from companies where context = '%s'", context)))
    return db:fetch({}, "a")
end

function get_extension(extension, context)
    db = assert(con:execute(string.format("SELECT pbx_endpoints.*, companies.id as company_id from pbx_endpoints inner join companies on pbx_endpoints.user_context = companies.context where auth_id= '%s' and user_context ='%s'", extension, context)))
    return db:fetch({}, "a")
end

function get_ivr(route,context)
    db = assert(con:execute(string.format("SELECT * from pbx_ivrs where context= '%s' and name ='%s'", context, route["name"])))
    return db:fetch({}, "a")
end

function get_tts(route,context)
    db = assert(con:execute(string.format("SELECT * from pbx_tts where context = '%s' and id = %d", context, tonumber(route["data"]))))
    return db:fetch({}, "a")
end

function get_outbound_caller_id(user_name, context)
    db = assert(con:execute(string.format("SELECT pbx_endpoints.outbound_caller_id_name as ext_name, pbx_endpoints.outbound_caller_id_number as ext_number, pbx_endpoints.user_id as user_id, companies.tel as tel, companies.name as company_name, companies.default_gateway as gateway, companies.id as company_id from pbx_endpoints inner join companies on pbx_endpoints.user_context = companies.context  where companies.context= '%s' and pbx_endpoints.auth_id ='%s'", context, user_name)))
    return db:fetch({}, "a")
end

function get_virtual_group_members(route, context)
    local gmembers = ""
    db = assert(con:execute(string.format("SELECT * from pbx_group_members inner join pbx_groups on pbx_groups.id = pbx_group_members.pbx_group_id where pbx_groups.name='%s' and context='%s'", route["name"], context)))
    row = db:fetch ({}, "a")
    while row do
        for ext, gateway in rows(string.format("SELECT did, default_gateway as gateway from pbx_virtual_extensions inner join companies on companies.context=pbx_virtual_extensions.context where extension= '%s' and pbx_virtual_extensions.context = '%s'", row.extension, context)) do
            gmembers = gmembers .. ",[leg_delay_start=10,leg_timeout=15]sofia/gateway/" .. gateway .. "/" .. ext
            log(gmembers)
        end
        row = db:fetch (row, "a")
    end
    return gmembers
end

function get_sequential_group_members(route, context)
    db = assert(con:execute(string.format("SELECT * from pbx_group_members inner join pbx_groups on pbx_groups.id = pbx_group_members.pbx_group_id where pbx_groups.name='%s' and context='%s'", route["name"], context)))
    return db:fetch ({}, "a")
end

function do_cc(name, context)
    cc = get_cc(name, context)
    ccp = get_cc_position(name)
    cc_agents = get_cc_tier_agents(name)

    hold_time = tonumber(ccp["num"]) * tonumber(cc["approx_hold_time"])

    if (hold_time > 0) then
        hold_time = hold_time/tonumber(cc_agents["agent_num"])
    end

    log("agent num" .. cc_agents["agent_num"])

    cc_num = tonumber(ccp["num"])+1

    session:sleep(2000)
    if cc["audio_type"] == "1" then
        session:execute("playback", "${base_dir}/htdocs/vm/".. context .."/recordings/" .. cc["audio_name"])
    else
        tts = get_tts_by_id(cc["audio_name"], context)
        session:set_tts_parms("cepstral", tts["voice"])
        session:speak(tts["text"])
    end

    session:set_tts_parms("cepstral", "Allison")
    session:sleep(2000)

    log(cc["announce_position"])

    if (cc["announce_position"]=="t") then
        session:execute("playback", "ivr/ivr-you_are_number.wav")
        session:speak(tostring(cc_num))
        session:execute("playback", "ivr/ivr-in_line.wav")
        session:speak("Your estimated hold time is " .. tostring(hold_time)  .. " minutes.")
    end

    session:execute("callcenter", name .. "@" .. context)
end

function do_tod(name, context)
    db = assert(con:execute(string.format("SELECT * from pbx_tod_routes where context= '%s' and name ='%s'", context, name)))
    tod = db:fetch({}, "a")

    day = os.date("%w")
    hour = os.date("%H")
    minutes = os.date("%M")

    shour = string.sub(tod["time_start"], 2, 3)
    sminutes = string.sub(tod["time_start"], 5, 6)

    ehour = string.sub(tod['time_end'], 2, 3)
    eminutes = string.sub(tod["time_end"], 5, 6)

    if tonumber(tod["day_start"]) <= tonumber(day) and tonumber(tod["day_end"]) >= tonumber(day) then
        if tonumber(hour..minutes) >= tonumber(shour..sminutes) and tonumber(hour..minutes) <= tonumber(ehour..eminutes) then
            return send_route(get_route_by_id(tod["match_route_id"]), context)
        else
            return send_route(get_route_by_id(tod["nomatch_route_id"]), context)
        end
    else
        return send_route(get_route_by_id(tod["nomatch_route_id"]), context)
    end
end

function do_ivr(route, context)
    session:answer()
    ivr = get_ivr(route, context)

    while (session:ready() == true) do
        freeswitch.consoleLog("NOTICE", string.format("Caller has called pbx for %s\n", context))
        session:setAutoHangup(true)
        session:sleep(2000)

        digits = ""

        if ivr["audio_type"] == "2" then
            session:setInputCallback("key_press", "")
            tts = get_tts(ivr, context)
            session:set_tts_parms("cepstral", tts["voice"])
            session:sleep(1000)
            session:speak(tts["text"])
            session:sleep(tonumber(ivr["timeout"] .. "000"))
        elseif ivr["audio_type"] == "1" then
            path = "/usr/local/freeswitch/htdocs/vm/" .. context .. "/recordings/" .. ivr["data"]
            digits = session:playAndGetDigits(1, 4, 3, tonumber(ivr["timeout"].."000"), '', path, 'voicemail/vm-that_was_an_invalid_ext.wav', '\\d+')
        end

        if string.len(digits) > 1 then
            if digits == "411" then
                session:transfer("411", "XML", context)
            end

            keyed_route = get_route_by_ext(digits, context)
            if keyed_route == nil or ivr["direct_dial"] ~= "t" then
                session:execute("playback", "voicemail/vm-that_was_an_invalid_ext.wav")
            else
                send_route(keyed_route, context)
            end
        elseif string.len(digits) == 1 then
            opt_route = get_route_by_ivr_opt(digits, ivr['id'])

            if opt_route == nil then
                session:execute("playback", "voicemail/vm-that_was_an_invalid_ext.wav")
            else
                send_route(opt_route, context)
            end
        else
            send_route(get_route_by_id(ivr["timeout_destination"]), context)
        end

    end

end

function check_exists_available(extension, context)
    session:execute("set", "contact_exists=${user_exists(id " .. extension .. " ${domain})}")
    if(session:getVariable("contact_exists") == "false") then
        session:execute("playback", "voicemail/vm-that_was_an_invalid_ext.wav")
    else
        session:execute("set", "contact_available=${sofia_contact(sip.vwna.com/" .. extension .. "@${domain})}")
        contact_available = session:getVariable("contact_available")
        if(string.find(contact_available, "error")) then
            session:speak("I am sorry, that person is unavailable.")
            session:execute("voicemail", profle " ".. context .. " " .. extension)
        else
            session:sleep(2000)
            session:execute("playback", "ivr/ivr-hold_connect_call.wav")
            session:execute("set", "transfer_ringback=${hold_music}")
            bridge_local(get_route_by_ext(extension, context), context)
        end
    end
end

function bridge_local(route, context)

    ext = get_extension(route['name'], context)

    if (ext["find_me"]=="t") then
        transfer_local(route, context)
    end

    session:execute("set","user_id=" .. ext["user_id"])
    session:execute("set","company_id=" .. ext["company_id"])
    session:execute("set","call_timeout=" .. ext["call_timeout"])
    session:execute("set","continue_on_fail=true")
    session:execute("set","hangup_after_bridge=true")
    session:execute("set","ringback=%(2000,4000,440.0,480.0)")

    if ext["record_inbound_calls"] == "t" then
        session:execute("record_session", "${base_dir}/htdocs/vm/" .. context .. "/extension-recordings/".. ext["auth_id"] .. "_${uuid}_inbound_${strftime(%Y-%m-%d-%H-%M-%S)}.mp3")
    end

    session:execute("bridge","user/" .. route['name'] .. "@" .. context)
    if ext["timeout_destination"] == nil then
        session:answer()
        session:sleep(1000)
        session:execute("voicemail", "sip.vwna.com " .. context .. " " .. route['name'])
    else
        send_route(get_route_by_id(ext["timeout_destination"]), context)
    end
end

function bridge_external(route, context)
    log("bridge external")
    gw = get_default_gateway(context)

    session:execute("set","call_timeout=" .. route["timeout"])
    session:execute("set","continue_on_fail=true")
    session:execute("set","hangup_after_bridge=true")
    session:execute("set", "effective_caller_id_name=" .. caller_name)
    session:execute("set", "effective_caller_id_number=" .. caller_num)
    session:execute("set", "origination_caller_id_name=" .. caller_name)
    session:execute("set", "origination_caller_id_number=" .. caller_num)
    session:execute("set", "ringback=%(2000,4000,440.0,480.0)")
    session:execute("bridge","sofia/gateway/" .. gw["default_gateway"] .. "/" .. route["did"])
    send_route(get_route_by_id(route["timeout_destination"]), context)
    session:hangup()
end

function bridge_outbound(name, num, to)
    log("bridge outbound")
    gw = get_default_gateway(context)

    ext = get_extension(user_name, context)

    if ext["record_outbound_calls"] == "t" then
        session:execute("record_session", "${base_dir}/htdocs/vm/" .. context .. "/extension-recordings/${caller_id_number}_${uuid}_outbound_${strftime(%Y-%m-%d-%H-%M-%S)}.mp3")
    end

    session:execute("set","continue_on_fail=false")
    session:execute("set","hangup_after_bridge=true")
    session:execute("set", "ringback=%(2000,4000,440.0,480.0)")
    session:execute("set", "effective_caller_id_name=" .. name)
    session:execute("set", "effective_caller_id_number=" .. num)
    session:execute("set", "origination_caller_id_name=" .. name)
    session:execute("set", "origination_caller_id_number=" .. num)
    session:execute("bridge","sofia/gateway/" ..gw["default_gateway"] .."/" .. to)
    session:hangup()
end

function bridge_group(route, context)
    virtual_members = get_virtual_group_members(route, context)
    group = get_group(route["name"], context)
    session:sleep(1000)
    session:execute("playback", "ivr/ivr-please_hold_while_party_contacted.wav")
    session:setVariable("effective_caller_id_name", "PBX " .. route["name"])
    session:execute("set","call_timeout=" .. group["timeout"])

    if group["ring_strategy"] == "seq" then
        session:execute("set","ignore_early_media=true")
        session:execute("set","continue_on_fail=true")
        session:execute("set","hangup_after_bridge=true")
        session:execute("set", "ringback=%(2000,4000,440.0,480.0)")

        db = assert(con:execute(string.format("SELECT * from pbx_group_members inner join pbx_groups on pbx_groups.id = pbx_group_members.pbx_group_id where pbx_groups.name='%s' and context='%s' order by pbx_group_members.id", route["name"], context)))
        row = db:fetch ({}, "a")
        while row do
            session:execute("set","call_timeout=13")
            session:execute("bridge","user/" .. row.extension .. "@" .. context)
            row = db:fetch (row, "a")
        end
        db = assert(con:execute(string.format("SELECT * from pbx_group_members inner join pbx_groups on pbx_groups.id = pbx_group_members.pbx_group_id where pbx_groups.name='%s' and context='%s'", route["name"], context)))
        row = db:fetch ({}, "a")
        while row do
            for ext, gateway in rows(string.format("SELECT did, default_gateway as gateway from pbx_virtual_extensions inner join companies on companies.context=pbx_virtual_extensions.context where extension= '%s' and pbx_virtual_extensions.context = '%s'", row.extension, context)) do
                session:execute("set","call_timeout=13")
                session:execute("bridge","sofia/gateway/".. gateway .."/"..ext)
            end
            row = db:fetch (row, "a")
        end
        session:execute("bridge", virtual_members)
        send_route(get_route_by_id(group["no_answer_destination"]), context)
    else
        log("group/" .. route["name"] .. "@" .. context .. virtual_members)
        session:execute("set","call_timeout=12")
        session:execute("set","continue_on_fail=true")
        session:execute("set","hangup_after_bridge=true")
        session:execute("set", "ringback=%(2000,4000,440.0,480.0)")
        session:execute("bridge","group/" .. route["name"] .. "@" .. context .. virtual_members)
        send_route(get_route_by_id(group["no_answer_destination"]), context)
    end
    session:hangup()
end

function transfer_local(route, context)
    session:answer()
    session:setAutoHangup(false)
    session:sleep(1000)
    session:execute("transfer", route['name'] .. " XML" .. " " .. context)
end



function send_route(route, context)
    log(route["name"])
    if route["pbx_route_type_id"] == "1" then
        check_exists_available(route["name"], context)
    elseif route["pbx_route_type_id"] == "2" then
        bridge_external(get_virtual_extension(route, context), context)
    elseif route["pbx_route_type_id"] == "3" then
        session:transfer(route["name"], "XML", context)
    elseif route["pbx_route_type_id"] == "4" then
        bridge_group(route, context)
    elseif route["pbx_route_type_id"] == "5" then
        do_ivr(route, context)
    elseif route["pbx_route_type_id"] == "6" then
        do_tod(route["name"], context)
    elseif route["pbx_route_type_id"] == "7" then
        session:execute("set", "called_num=" .. route["name"])
        session:transfer(route["name"], "XML", context)
    elseif route["pbx_route_type_id"] == "10" then
        do_cc(route["name"], context)
    elseif route["pbx_route_type_id"] == "11" then
        session:transfer(route["name"], "XML", context)
    elseif route["pbx_route_type_id"] == "12" then
        session:transfer(route["name"], "XML", context)
    else
    end
end

--[[
     Set all the incoming variables. Todo: local the variables and pass
     as parameters to prevent namespace collisions etc.
--]]

session:setHangupHook("session_hangup_hook")
context = session:getVariable("context")
is_outbound = session:getVariable("is_outbound")
is_inbound = session:getVariable("is_inbound")
user_name = session:getVariable("user_name")
is_authed = session:getVariable("sip_authorized")
session:execute("set", "domain=" .. context)
session:execute("set", "domain_name=" .. context)
session:execute("set", "user_context=" .. context)
session:execute("set", "force_transfer_context=" .. context)
session:execute("set", "force_transfer_dialplan=XML")
called_num = session:getVariable("destination_number")
caller_num = session:getVariable("caller_id_number")
caller_name = session:getVariable("caller_id_name")
profile = session:getVariable("variable_sofia_profile_name")

log(called_num)

--[[

    Inbound/Outbound routes

]]--

if is_inbound then
    session:execute("set", "call_direction=inbound")
    if string.len(caller_num)> 10 then
        caller_num = string.sub(caller_num, string.len(caller_num)-9, string.len(caller_num))
    end

    if blacklisted(caller_num, context) then
        session:hangup()
    end

    get_cid_route(caller_num, context)
    send_route(get_route_by_did(called_num), context)
end

if is_outbound and is_authed then
    session:execute("set", "call_direction=outbound")
    session:execute("set", "extension=" .. user_name)
    row = get_outbound_caller_id(user_name, context)
    session:execute("set", "company_id=" .. row["company_id"])
    session:execute("set", "user_id=" .. row["user_id"])
    if string.len(row["ext_number"]) == 10 then
        bridge_outbound(row["ext_name"], row["ext_number"], called_num)
    else
        bridge_outbound(row["company_name"], row["tel"], called_num)
    end
end