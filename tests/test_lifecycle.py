"""Mock reflected ownership and UMG; does not establish live rendering/performance."""
import sys
from pathlib import Path
if len(sys.argv)>1:
    sys.path.insert(0, sys.argv[1])
from lupa import LuaRuntime
lua = LuaRuntime()
lua.execute(r'''
shared={}; scans=0; writes=0; timers={}; viewport={X=3440,Y=1440}; nextAddress=0; logs={}; layouts=0
function print(s) logs[#logs+1]=s end
ModRef={GetSharedVariable=function(_,k) return shared[k] end,SetSharedVariable=function(_,k,v) shared[k]=v end}
function obj(t)
 t=t or {}; nextAddress=nextAddress+1; t.address=nextAddress
 t.GetAddress=function(s) return s.address end
 t.IsValid=function(s) return not s.dead end
 t.IsA=function(s,c) return not s.wrong end
 t.GetFullName=function(s) return s.name or 'Object runtime' end
 return t
end
gi=obj(); controller=obj(); hud=obj(); panel=obj(); canvas=obj(); slot=obj()
controller.IsLocalController=function() return true end
controller.GetHUD=function() return hud end
hud.AlwaysVisibleCanvas=panel; panel.GetParent=function() return canvas end
radarWrites=0; childReads=0
radarSlot=obj({offsets={Left=196,Top=-112,Right=940,Bottom=940}})
radarSlot.GetAnchors=function() return {Minimum={X=0,Y=1},Maximum={X=0,Y=1}} end
radarSlot.GetOffsets=function(s) return s.offsets end
radarSlot.SetOffsets=function(s,v) radarWrites=radarWrites+1; s.offsets=v end
radar=obj({Slot=radarSlot,RenderTransform={Translation={X=0,Y=0}}})
radar.GetFName=function() return {ToString=function() return 'MIniMapCanvas' end} end
radar.SetRenderTranslation=function(s,v) radarWrites=radarWrites+1; s.RenderTransform.Translation=v end
portraitWrites=0
portraitSlot=obj({offsets={Left=-616,Top=180,Right=420,Bottom=532}})
portraitSlot.GetAnchors=function(s) return {Minimum={X=s.badanchor and 0 or 1,Y=0},Maximum={X=1,Y=0}} end
portraitSlot.GetOffsets=function(s) return s.offsets end
portraitSlot.GetAlignment=function() return {X=0,Y=0} end
portraitSlot.GetAutoSize=function() return false end
portraitSlot.SetOffsets=function(s,v) portraitWrites=portraitWrites+1; s.offsets=v end
portrait=obj({Slot=portraitSlot,RenderTransform={Translation={X=0,Y=0}}})
portrait.SetRenderTranslation=function(s,v)
 if portraitFailure then error('translation failure') end
 portraitWrites=portraitWrites+1; s.RenderTransform.Translation=v
end
message=obj({CanvasPanel_ComPortrait=portrait})
message.GetFName=function() return {ToString=function() return 'HUDMessageWidget' end} end
panel.GetChildrenCount=function() childReads=childReads+1; return radarMissing and 1 or 2 end
panel.GetChildAt=function(_,i) if radarMissing or i==1 then return message else return radar end end
function checkPortrait()
 local width=math.max(3840,2160*viewport.X/viewport.Y)
 local scale=viewport.Y/2160
 local margin=(viewport.X-3840*scale)/2
 -- Reconstruct the native rectangle calculation and the widened UMG draw.
 local maskLeft=margin+(3840+portraitSlot.offsets.Left)*scale
 local drawnLeft=(width+portraitSlot.offsets.Left+portrait.RenderTransform.Translation.X)*scale
 assert(math.abs(maskLeft-drawnLeft)<0.01, 'portrait mask must match visible portrait')
 assert(math.abs(drawnLeft-(width-616)*scale)<0.01, 'visible portrait must not move')
end
function newslot()
 local s=obj({width=3840,height=2160})
 s.GetAnchors=function(self) layouts=layouts+1; local x=self.badanchor and 0 or .5; return {Minimum={X=x,Y=.5},Maximum={X=.5,Y=.5}} end
 s.GetAlignment=function() return {X=.5,Y=.5} end
 s.GetAutoSize=function() return false end
 s.GetOffsets=function(self) return {Left=0,Top=0,Right=self.width,Bottom=self.height} end
 s.SetSize=function(self,v) writes=writes+1; self.width=v.X; self.height=v.Y end
 return s
end
slot=newslot(); canvas.Slot=slot
canvas.GetFName=function() return {ToString=function() return 'MainCanvas' end} end
statics=obj({GetPlayerController=function() return controller end})
layout=obj({GetViewportSize=function() return viewport end})
function StaticFindObject(path) if path:find('GameplayStatics') then return statics else return layout end end
function FindFirstOf() scans=scans+1; return gi end
cameraScans=0; notifications={}
function FindAllOf() cameraScans=cameraScans+1; return {} end
function NotifyOnNewObject(path,f)
 notifications[path]=f
 if path=='/Script/Engine.GameInstance' then notify=f end
end
function ExecuteInGameThread(f) f() end
function LoopInGameThreadWithDelay(ms,f) assert(ms==500); timers[#timers+1]=f; tick=f end
''')
source=(Path(__file__).resolve().parents[1]/'mod/Scripts/main.lua').read_text()
lua.execute(source)
lua.execute(r'''
tick(); assert(writes==1 and slot.width==5160)
checkPortrait()
local initialPortraitWrites=portraitWrites
assert(radarSlot.offsets.Left==-464 and radar.RenderTransform.Translation.X==660)
assert(radarSlot.offsets.Left+radar.RenderTransform.Translation.X==196)
local initialRadarWrites,initialChildReads=radarWrites,childReads
local logCount,layoutCount=#logs,layouts
for i=1,1000 do
 -- Fresh unequal Lua wrappers still refer to the same underlying Unreal object.
 canvas.Slot=setmetatable({}, {__index=slot})
 tick()
end
canvas.Slot=slot
assert(writes==1 and scans==1, 'stable checks must not scan or write')
assert(radarWrites==initialRadarWrites and childReads==initialChildReads, 'stable radar must not enumerate children or write')
assert(portraitWrites==initialPortraitWrites, 'stable portrait must not write')
assert(#logs==logCount and layouts==layoutCount, 'fresh wrappers must not trigger logging or layout revalidation')
local previous=slot; slot=newslot(); canvas.Slot=slot
tick(); assert(writes==2 and slot.width==5160 and previous:IsValid(), 'replace even if old object remains valid')
viewport={X=5120,Y=1440}; tick(); assert(writes==3 and slot.width==7680)
checkPortrait()
assert(radarSlot.offsets.Left==-1724 and radar.RenderTransform.Translation.X==1920)
viewport={X=1920,Y=1080}; tick(); assert(writes==4 and slot.width==3840)
checkPortrait()
assert(portraitSlot.offsets.Left==-616 and portrait.RenderTransform.Translation.X==0)
assert(radarSlot.offsets.Left==196 and radar.RenderTransform.Translation.X==0)
viewport={X=0,Y=0}; tick(); assert(writes==4)
viewport={X=3440,Y=1440}; local original=hud; hud=obj({wrong=true})
tick(); assert(writes==4, 'menus must not change')
hud=original; slot=newslot(); slot.badanchor=true; canvas.Slot=slot
tick(); assert(writes==4, 'unknown layouts must be skipped')
slot=newslot(); canvas.Slot=slot; tick(); assert(writes==5)
gi.dead=true; tick(); assert(writes==5)
gi=obj(); notify(gi); tick(); assert(writes==5 and scans==1)
assert(slot.width==5160)
''')
lua.execute(source)
lua.execute(r'''
local old=timers[1]; slot=newslot(); canvas.Slot=slot
old(); assert(writes==5, 'old reload callback must be inert')
tick(); assert(writes==6 and slot.width==5160)
local count=#logs
local get=controller.GetHUD
controller.GetHUD=function() error('transient failure') end
tick(); assert(#logs==count+1)
controller.GetHUD=get; tick()
controller.GetHUD=function() error('different failure') end
for i=1,100 do tick() end
assert(#logs==count+1, 'intermittent/different errors must not spam logs')
controller.GetHUD=get; tick()
radarMissing=true; slot=newslot(); canvas.Slot=slot; tick()
radarSlot.offsets.Left=196; radar.RenderTransform.Translation.X=0
radarMissing=false; tick()
assert(radarSlot.offsets.Left==-464 and radar.RenderTransform.Translation.X==660, 'late radar construction must retry')
local rw=radarWrites
tick(); assert(radarWrites==rw, 'correction must not accumulate')
checkPortrait()
message.CanvasPanel_ComPortrait=nil; slot=newslot(); canvas.Slot=slot; tick()
portraitSlot.offsets.Left=-616; portrait.RenderTransform.Translation.X=0
message.CanvasPanel_ComPortrait=portrait; tick(); checkPortrait()
local pw=portraitWrites; tick(); assert(portraitWrites==pw, 'late portrait correction must settle')
portraitSlot.badanchor=true; slot=newslot(); canvas.Slot=slot; tick()
assert(portraitWrites==pw, 'unknown portrait layouts must not be modified')
portraitSlot.badanchor=false; slot=newslot(); canvas.Slot=slot
portraitSlot.offsets.Left=-616; portrait.RenderTransform.Translation.X=0
portraitFailure=true; tick()
assert(portraitSlot.offsets.Left==-616 and portrait.RenderTransform.Translation.X==0, 'failed translation must roll back layout')
portraitFailure=false; tick(); checkPortrait()
''')
print('PASS: stable checks, stale valid HUD, resolution changes, narrow/zero viewport, menus, unknown layout, GameInstance replacement, reload ownership')
lua.execute(r'''
controller.PlayerCameraManager=obj({bDefaultConstrainAspectRatio=true})
local camera=obj({AspectRatio=16/9,bConstrainAspectRatio=true})
camera.SetConstraintAspectRatio=function(s,v) s.bConstrainAspectRatio=v end
camera.SetAspectRatioAxisConstraint=function(s,v) s.axis=v end
local sequence=obj()
notifications['/Script/Engine.CameraComponent'](camera)
notifications['/Script/LevelSequence.LevelSequencePlayer'](sequence)
viewport={X=3440,Y=1440}; tick()
assert(not camera.bConstrainAspectRatio and not controller.PlayerCameraManager.bDefaultConstrainAspectRatio)
assert(camera.axis==nil and sequence.CameraSettings==nil, 'projection threshold must be respected')
viewport={X=5120,Y=1440}; tick()
assert(camera.bOverrideAspectRatioAxisConstraint and camera.axis==0)
assert(sequence.CameraSettings.bOverrideAspectRatioAxisConstraint and sequence.CameraSettings.AspectRatioAxisConstraint==0)
viewport={X=1920,Y=1080}; tick()
assert(camera.axis==0 and sequence.CameraSettings.AspectRatioAxisConstraint==0, 'current implementation retains projection overrides')
camera.dead=true; sequence.dead=true; tick()
assert(cameraScans==4, 'only two bootstrap scans per initialization')
''')
print('PASS: camera notifications, constraint removal, projection threshold, retained overrides and invalid-object cleanup')
