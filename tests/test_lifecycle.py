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
function NotifyOnNewObject(_,f) notify=f end
function ExecuteInGameThread(f) f() end
function LoopInGameThreadWithDelay(ms,f) assert(ms==500); timers[#timers+1]=f; tick=f end
''')
source=(Path(__file__).resolve().parents[1]/'mod/Scripts/main.lua').read_text()
lua.execute(source)
lua.execute(r'''
tick(); assert(writes==1 and slot.width==5160)
local logCount,layoutCount=#logs,layouts
for i=1,1000 do
 -- Fresh unequal Lua wrappers still refer to the same underlying Unreal object.
 canvas.Slot=setmetatable({}, {__index=slot})
 tick()
end
canvas.Slot=slot
assert(writes==1 and scans==1, 'stable checks must not scan or write')
assert(#logs==logCount and layouts==layoutCount, 'fresh wrappers must not trigger logging or layout revalidation')
local previous=slot; slot=newslot(); canvas.Slot=slot
tick(); assert(writes==2 and slot.width==5160 and previous:IsValid(), 'replace even if old object remains valid')
viewport={X=5120,Y=1440}; tick(); assert(writes==3 and slot.width==7680)
viewport={X=1920,Y=1080}; tick(); assert(writes==4 and slot.width==3840)
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
''')
print('PASS: stable checks, stale valid HUD, resolution changes, narrow/zero viewport, menus, unknown layout, GameInstance replacement, reload ownership')
