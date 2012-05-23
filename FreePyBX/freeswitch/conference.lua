require "luasql.postgres"

--[[
    Tightly based on the FreeSWITCH Project simple lua conference example.
--]]

attempt = 1
max_attempts = 3

function session_hangup_hook(status)
    freeswitch.consoleLog("NOTICE", "Session hangup: " .. status .. "\n")
    db_connection:close()
    error()
end

function log(logval)
    freeswitch.consoleLog("NOTICE", "----------------->" .. tostring(logval) .. " <------------- \n")
end

function get_conference_num(min, max, attempts, timeout)
    local conference_num
    freeswitch.consoleLog("NOTICE", "Awaiting caller to enter a conference number phrase:conference_num\n")
    conference_num = session:playAndGetDigits(min, max, attempts, timeout, '#', 'phrase:conference_num', '', '\\d+')
    return(conference_num)
end

function get_conference_pin(min, max, attempts, timeout, pin_number)
    local pin_attempt = 1
    local pin_max_attempt = 3

    while pin_attempt <= pin_max_attempt do
        conference_pin = session:playAndGetDigits(min, max, attempts, timeout, '#', 'phrase:conference_pin', '', '\\d+')
        if tonumber(conference_pin) == tonumber(pin_number) then
            return true
        else
            session:execute("phrase", "conference_bad_pin")
        end

        pin_attempt = pin_attempt + 1
    end

    return false
end

env = assert(luasql.postgres())
db_connection = assert(env:connect("dbname=pbx user=pbxuser password=secretpass1 host=127.0.0.1"))

session:answer()
session:setHangupHook("session_hangup_hook")

context = session:getVariable("context")
called_num = session:getVariable("called_num")

if session:ready() then
    freeswitch.consoleLog("NOTICE", string.format("Caller has called conferencing server, Playing welcome message phrase:conference_welcome\n"))
    session:execute("phrase", "conference_welcome")
end

log(called_num)

while attempt <= max_attempts do
    conf_num = called_num --get_conference_num(1, 4, 3, 4000)

    db_cursor = assert(db_connection:execute(string.format("select pin from sip_conference_bridges where extension = '%s' and context='%s'", tostring(conf_num), context)))
    row = db_cursor:fetch({}, "a")

    --[[ do conference authentication ]]--
    if row == nil then
        --[[ if the conference number does not exist, playback message saying it is
    and invalid conference number ]]--
        session:execute("phrase", "conference_bad_num")

    elseif row["pin"] == nil or row["pin"] == "" then
        freeswitch.consoleLog("NOTICE", string.format("Conference %d has no PIN, Sending caller into conference\n", tonumber(conf_num)))

        --[[ join the conference ]]--
        session:execute("conference", string.format("%s@%s", conf_num, context))
    else
        freeswitch.consoleLog("NOTICE", string.format("Conference %d has a PIN %d, Authenticating user\n", tonumber(conf_num), tonumber(row["pin"])))

        --[[ get the conference pin number ]]--
        if ((get_conference_pin(1, 4, 3, 4000, row["pin"])) == true) then
            freeswitch.consoleLog("NOTICE", string.format("Conference %d correct PIN entered, Sending caller into conference\n", tonumber(conf_num)))
            --[[ join the conference, if the correct pin was entered ]]--
            session:execute("conference", string.format("%s@sip.vwna.com", conf_num))
        else
            freeswitch.consoleLog("NOTICE", string.format("Conference %d invalid PIN entered, Looping again\n", tonumber(conf_num)))
        end
    end

    attempt = attempt + 1
end

session:execute("phrase", "conference_too_many_failures")

