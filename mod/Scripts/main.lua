-- AC8UltrawideHUD 0.1.1: gameplay MainCanvas only.
local generation = (ModRef:GetSharedVariable("AC8UltrawideHUD.Generation") or 0) + 1
ModRef:SetSharedVariable("AC8UltrawideHUD.Generation", generation)
local function current() return ModRef:GetSharedVariable("AC8UltrawideHUD.Generation") == generation end
local function valid(o) return o ~= nil and o:IsValid() end
local function log(s) print("[AC8UltrawideHUD] " .. s .. "\n") end
local gameInstance, statics, layout, activeSlot
local activeAddress, lastX, lastY, supported
local reported = {}
local function warnOnce(kind, message)
    if not reported[kind] then reported[kind]=true; log(message) end
end
local function remember(o)
    if current() and valid(o) and not o:GetFullName():find("Default__",1,true) then
        gameInstance=o
    end
end
NotifyOnNewObject("/Script/Engine.GameInstance", function(o)
    ExecuteInGameThread(function() remember(o) end)
end)
-- One bootstrap scan handles loading the mod after the GameInstance exists.
-- Subsequent instances are discovered by notification, never periodic scans.
ExecuteInGameThread(function()
    if not current() then return end
    if not valid(gameInstance) then remember(FindFirstOf("BP_LiveGameInstance_C")) end
end)
local function clear()
    activeSlot=nil; activeAddress=nil; supported=nil; lastX=nil; lastY=nil
end
local function check()
    if not valid(gameInstance) then clear(); return end
    if not valid(statics) then statics=StaticFindObject("/Script/Engine.Default__GameplayStatics") end
    if not valid(layout) then layout=StaticFindObject("/Script/UMG.Default__WidgetLayoutLibrary") end
    if not valid(statics) or not valid(layout) then return end
    local controller=statics:GetPlayerController(gameInstance,0)
    if not valid(controller) or not controller:IsLocalController() then clear(); return end
    local hud=controller:GetHUD()
    if not valid(hud) or not hud:IsA("/Script/Live.LiveHUD") then clear(); return end
    local panel=hud.AlwaysVisibleCanvas
    if not valid(panel) then clear(); return end
    local canvas=panel:GetParent()
    if not valid(canvas) then clear(); return end
    local slot=canvas.Slot
    if not valid(slot) then clear(); return end
    local viewport=layout:GetViewportSize(canvas)
    if viewport.X<=0 or viewport.Y<=0 then return end
    -- UE4SS versions can create unequal Lua wrappers for the same UObject.
    local address=slot:GetAddress()
    local changed = not valid(activeSlot) or activeAddress ~= address
    if changed then
        activeSlot=slot; activeAddress=address; lastX=nil; lastY=nil; supported=false
        if canvas:GetFName():ToString() ~= "MainCanvas" or not slot:IsA("/Script/UMG.CanvasPanelSlot") then
            warnOnce("container","Skipped unfamiliar HUD container"); return
        end
        local a,p,o=slot:GetAnchors(),slot:GetAlignment(),slot:GetOffsets()
        local desired=math.max(3840,2160*viewport.X/viewport.Y)
        supported = a.Minimum.X==0.5 and a.Maximum.X==0.5 and a.Minimum.Y==0.5 and a.Maximum.Y==0.5
            and p.X==0.5 and p.Y==0.5 and not slot:GetAutoSize()
            and math.abs(o.Left)<0.01 and math.abs(o.Top)<0.01 and math.abs(o.Bottom-2160)<0.01
            and (math.abs(o.Right-3840)<0.1 or math.abs(o.Right-desired)<0.1)
        if not supported then warnOnce("layout","Skipped unfamiliar MainCanvas layout"); return end
    end
    if not supported then return end
    if not changed and lastX==viewport.X and lastY==viewport.Y then return end
    local width=math.max(3840,2160*viewport.X/viewport.Y)
    local offsets=slot:GetOffsets()
    if math.abs(offsets.Right-width)>0.1 then
        slot:SetSize({X=width,Y=2160})
    end
    lastX=viewport.X; lastY=viewport.Y
end
LoopInGameThreadWithDelay(500,function()
    if not current() then return end
    local ok,err=pcall(check)
    if not ok then
        -- Permit retry after transient world teardown, without repeating the log.
        clear()
        warnOnce("error","Waiting after layout error (further errors suppressed): "..tostring(err))
    end
end)
log("Ready: gameplay HUD only; checks every 500 ms, applies on canvas or resolution change")
