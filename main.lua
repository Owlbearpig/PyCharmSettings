--
-- Created by IntelliJ IDEA.
-- User: POTATO
-- Date: 5/21/2018
-- Time: 12:45 AM
-- To change this template use File | Settings | File Templates.
--

local string arg1, arg2, arg3 = CalendarGetDate()
local int cur_day = arg3
local int cur_month = arg2

function release_date ()

    local t = {}
    t[5] = 31
    t[6] = 30
    t[7] = 30
    t[8] = 14

    local r = {}
    r[5] =  t[6] + t[7] + t[8]
    r[6] =  t[7] + t[8]
    r[7] =  t[8]

    local m_end = t[cur_month] - cur_day

    local total = m_end + r[cur_month]

    local gmotd = ""
    gmotd = gmotd.format("%i %s", total, "days until bfa release = )")

    return gmotd, total

end

local string f, total = release_date()
local string cur_motd = GetGuildRosterMOTD()

local int cur_motd_date = tonumber(cur_motd.sub(cur_motd, 1, 2))
local int total = total

if cur_motd_date ~= total then
    SendChatMessage(f, "OFFICER")
    GuildSetMOTD(f)
end



