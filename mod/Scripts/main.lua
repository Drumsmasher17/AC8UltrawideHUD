-- AC8UltrawideHUD 0.1.3: ultrawide HUD/masks and cinematic camera adjustments.
local generation = (ModRef:GetSharedVariable("AC8UltrawideHUD.Generation") or 0) + 1
ModRef:SetSharedVariable("AC8UltrawideHUD.Generation", generation)
local function current() return ModRef:GetSharedVariable("AC8UltrawideHUD.Generation") == generation end
local function valid(o) return o ~= nil and o:IsValid() end
local function log(s) print("[AC8UltrawideHUD] " .. s .. "\n") end
local gameInstance, statics, layout, activeSlot
local activeAddress, lastX, lastY, supported
local radarReady=false
local portraitReady=false
local reported = {}
local function warnOnce(kind, message)
    if not reported[kind] then reported[kind]=true; log(message) end
end
local cameras, cameraAddresses = {}, {}
local function trackCamera(camera)
    if not current() or not valid(camera) then return end
    local address=camera:GetAddress()
    if not cameraAddresses[address] then
        cameraAddresses[address]=true
        cameras[#cameras+1]={object=camera,address=address,aspect=camera.AspectRatio,
            constrained=camera.bConstrainAspectRatio}
    end
end
NotifyOnNewObject("/Script/Engine.CameraComponent", function(camera)
    ExecuteInGameThread(function() trackCamera(camera) end)
end)
local sequencePlayers, sequencePlayerAddresses = {}, {}
local function trackSequencePlayer(player)
    if not current() or not valid(player) then return end
    local address=player:GetAddress()
    if not sequencePlayerAddresses[address] then
        sequencePlayerAddresses[address]=true
        sequencePlayers[#sequencePlayers+1]={object=player,address=address}
    end
end
NotifyOnNewObject("/Script/LevelSequence.LevelSequencePlayer", function(player)
    ExecuteInGameThread(function() trackSequencePlayer(player) end)
end)
local function removeCameraBars(controller)
    local ok,err=pcall(function()
        local manager=controller.PlayerCameraManager
        if valid(manager) and manager.bDefaultConstrainAspectRatio then
            manager.bDefaultConstrainAspectRatio=false
        end
        local viewport=layout:GetViewportSize(controller)
        local wideViewport=viewport.Y>0 and viewport.X/viewport.Y>2.4
        -- Keep the sequence's animated focal length, but constrain projection
        -- on the vertical axis so widening the viewport reveals more horizontally.
        for i=#cameras,1,-1 do
            local entry=cameras[i]
            local camera=entry.object
            if not valid(camera) then
                cameraAddresses[entry.address]=nil
                table.remove(cameras,i)
            else
                if camera.bConstrainAspectRatio then
                    entry.constrained=true
                    camera:SetConstraintAspectRatio(false)
                end
                if wideViewport and entry.constrained then
                    camera.bOverrideAspectRatioAxisConstraint=true
                    camera:SetAspectRatioAxisConstraint(0)
                end
            end
        end
        for i=#sequencePlayers,1,-1 do
            local entry=sequencePlayers[i]
            local player=entry.object
            if not valid(player) then
                sequencePlayerAddresses[entry.address]=nil
                table.remove(sequencePlayers,i)
            elseif wideViewport then
                player.CameraSettings={
                    bOverrideAspectRatioAxisConstraint=true,
                    AspectRatioAxisConstraint=0
                }
            end
        end
    end)
    if not ok then warnOnce("camera","Could not disable cinematic camera bars: "..tostring(err)) end
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
    local existingCameras=FindAllOf("CameraComponent")
    if existingCameras then
        for _,camera in pairs(existingCameras) do trackCamera(camera) end
    end
    local existingSequencePlayers=FindAllOf("LevelSequencePlayer")
    if existingSequencePlayers then
        for _,player in pairs(existingSequencePlayers) do trackSequencePlayer(player) end
    end
end)
local function clear()
    activeSlot=nil; activeAddress=nil; supported=nil; lastX=nil; lastY=nil
    radarReady=false
    portraitReady=false
end
local function correctPortrait(panel,width)
    local message
    for i=0,panel:GetChildrenCount()-1 do
        local child=panel:GetChildAt(i)
        if valid(child) and child:GetFName():ToString()=="HUDMessageWidget" then message=child; break end
    end
    if not valid(message) then return false end
    local portrait=message.CanvasPanel_ComPortrait
    if not valid(portrait) then return false end
    local slot=portrait.Slot
    if not valid(slot) then return false end
    if not slot:IsA("/Script/UMG.CanvasPanelSlot") then
        warnOnce("portrait","Skipped unfamiliar portrait layout"); return true
    end
    local a,o,p=slot:GetAnchors(),slot:GetOffsets(),slot:GetAlignment()
    local t=portrait.RenderTransform.Translation
    if a.Minimum.X~=1 or a.Maximum.X~=1 or a.Minimum.Y~=0 or a.Maximum.Y~=0
        or p.X~=0 or p.Y~=0 or slot:GetAutoSize()
        or math.abs(o.Left+t.X+616)>0.1 or math.abs(o.Top-180)>0.1
        or math.abs(o.Right-420)>0.1 or math.abs(o.Bottom-532)>0.1 or math.abs(t.Y)>0.1 then
        warnOnce("portrait","Skipped unfamiliar portrait layout"); return true
    end
    -- Native mask positioning uses a centred 3840-wide canvas, ignoring the
    -- widened parent and render translation. A right anchor needs +delta;
    -- the opposite render translation keeps the visible portrait in place.
    local delta=(width-3840)/2
    if math.abs(o.Left-(-616+delta))>0.1 or math.abs(t.X+delta)>0.1 then
        local original={Left=o.Left,Top=o.Top,Right=o.Right,Bottom=o.Bottom}
        slot:SetOffsets({Left=-616+delta,Top=o.Top,Right=o.Right,Bottom=o.Bottom})
        local ok,err=pcall(function() portrait:SetRenderTranslation({X=-delta,Y=t.Y}) end)
        if not ok then slot:SetOffsets(original); error(err) end
    end
    return true
end
local function correctRadar(panel,width)
    -- Bounded direct children only, on HUD creation/resolution change.
    -- A missing radar is retried while the HUD finishes constructing.
    local radar
    for i=0,panel:GetChildrenCount()-1 do
        local child=panel:GetChildAt(i)
        if valid(child) and child:GetFName():ToString()=="MIniMapCanvas" then radar=child; break end
    end
    if not valid(radar) then return false end
    local slot=radar.Slot
    if not valid(slot) then return false end
    if not slot:IsA("/Script/UMG.CanvasPanelSlot") then return true end
    local a,o=slot:GetAnchors(),slot:GetOffsets()
    local t=radar.RenderTransform.Translation
    if a.Minimum.X~=0 or a.Maximum.X~=0 or a.Minimum.Y~=1 or a.Maximum.Y~=1
        or math.abs(o.Left+t.X-196)>0.1 or math.abs(o.Top+112)>0.1
        or math.abs(o.Right-940)>0.1 or math.abs(o.Bottom-940)>0.1 or math.abs(t.Y)>0.1 then
        warnOnce("radar","Skipped unfamiliar radar layout"); return true
    end
    -- Native compositing adds the old 16:9 side margin to these offsets.
    -- Cancel it in layout, then restore the drawing position with translation.
    -- The game refreshes the mask when radar mode changes.
    local delta=(width-3840)/2
    if math.abs(o.Left-(196-delta))>0.1 or math.abs(t.X-delta)>0.1 then
        local original={Left=o.Left,Top=o.Top,Right=o.Right,Bottom=o.Bottom}
        slot:SetOffsets({Left=196-delta,Top=o.Top,Right=o.Right,Bottom=o.Bottom})
        local ok,err=pcall(function() radar:SetRenderTranslation({X=delta,Y=t.Y}) end)
        if not ok then slot:SetOffsets(original); error(err) end
    end
    return true
end
local function check()
    if not valid(gameInstance) then clear(); return end
    if not valid(statics) then statics=StaticFindObject("/Script/Engine.Default__GameplayStatics") end
    if not valid(layout) then layout=StaticFindObject("/Script/UMG.Default__WidgetLayoutLibrary") end
    if not valid(statics) or not valid(layout) then return end
    local controller=statics:GetPlayerController(gameInstance,0)
    if not valid(controller) or not controller:IsLocalController() then clear(); return end
    removeCameraBars(controller)
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
        radarReady=false
        portraitReady=false
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
    if not changed and lastX==viewport.X and lastY==viewport.Y and radarReady and portraitReady then return end
    local width=math.max(3840,2160*viewport.X/viewport.Y)
    local offsets=slot:GetOffsets()
    if math.abs(offsets.Right-width)>0.1 then
        slot:SetSize({X=width,Y=2160})
    end
    radarReady=correctRadar(panel,width)
    portraitReady=correctPortrait(panel,width)
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
log("Ready: ultrawide HUD/masks and cinematic camera adjustments; checks every 500 ms; HUD applies on canvas or resolution change")
