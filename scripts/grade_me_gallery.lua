-- Run from DaVinci Resolve's Workspace > Console (Lua):
-- dofile("/Users/malekhassan/Desktop/personalwebsite/scripts/grade_me_gallery.lua")
--
-- The script imports the curated originals, applies restrained per-scene CDL
-- grades, and exports metadata-free JPEG stills for the website gallery.

local resolve = Resolve()
local projectManager = resolve:GetProjectManager()
local project = projectManager:GetCurrentProject()

assert(project, "Open the personalwebsite-me-gallery project before running this script")

local mediaStorage = resolve:GetMediaStorage()
local mediaPool = project:GetMediaPool()
local gallery = project:GetGallery()
local album = gallery:CreateGalleryStillAlbum()
local stagingDir = "/Users/malekhassan/Library/Containers/com.blackmagic-design.DaVinciResolveLite/Data/grade-input"
local outputDir = "/Users/malekhassan/Library/Containers/com.blackmagic-design.DaVinciResolveLite/Data/grade-output"

assert(album, "Unable to create a Resolve stills album")
gallery:SetAlbumName(album, "personalwebsite-me-gallery")
gallery:SetCurrentStillAlbum(album)

local grades = {
  daylight = {
    slope = "1.015 1.005 0.985",
    offset = "0.000 0.000 0.002",
    power = "0.985 0.990 1.000",
    saturation = "1.06"
  },
  night = {
    slope = "1.080 1.050 1.020",
    offset = "0.006 0.004 0.008",
    power = "0.960 0.980 1.000",
    saturation = "1.08"
  },
  gym = {
    slope = "1.030 1.010 0.980",
    offset = "-0.002 0.000 0.004",
    power = "0.980 0.990 1.000",
    saturation = "1.04"
  },
  indoor = {
    slope = "1.030 1.015 0.995",
    offset = "0.000 0.000 0.003",
    power = "0.980 0.990 1.000",
    saturation = "1.05"
  }
}

local picks = {
  { file = stagingDir .. "/HTHY8132.JPG", name = "me-01-roots", tall = false, grade = "daylight" },
  { file = stagingDir .. "/IMG_1071.HEIC", name = "me-02-pool", tall = false, grade = "indoor" },
  { file = stagingDir .. "/IMG_1297.HEIC", name = "me-03-training-partner", tall = true, grade = "gym" },
  { file = stagingDir .. "/IMG_1718.HEIC", name = "me-04-red-sea", tall = false, grade = "daylight" },
  { file = stagingDir .. "/IMG_1978.HEIC", name = "me-05-night-run", tall = false, grade = "night" },
  { file = stagingDir .. "/IMG_2174.HEIC", name = "me-06-gym-notes", tall = true, grade = "gym" },
  { file = stagingDir .. "/IMG_2650.HEIC", name = "me-07-after-the-run", tall = false, grade = "night" },
  { file = stagingDir .. "/IMG_4087.HEIC", name = "me-08-padel", tall = true, grade = "night" },
  { file = stagingDir .. "/IMG_4598.JPG", name = "me-09-old-friends", tall = false, grade = "daylight", rotation = -90 },
  { file = stagingDir .. "/IMG_4884.HEIC", name = "me-10-morning-session", tall = true, grade = "gym" },
  { file = stagingDir .. "/IMG_5408.HEIC", name = "me-11-code-campus", tall = false, grade = "indoor" },
  { file = stagingDir .. "/IMG_5465.HEIC", name = "me-12-berlin", tall = false, grade = "daylight" },
  { file = stagingDir .. "/IMG_5601.HEIC", name = "me-13-work-in-progress", tall = true, grade = "gym" },
  { file = stagingDir .. "/IMG_E0870.JPG", name = "me-14-rim", tall = true, grade = "night" },
  { file = stagingDir .. "/IMG_E0885.HEIC", name = "me-15-repeat", tall = true, grade = "gym" },
  { file = stagingDir .. "/IMG_E3758.JPG", name = "me-16-hang-time", tall = true, grade = "indoor" },
  { file = stagingDir .. "/IMG_E3867.JPG", name = "me-17-campus", tall = true, grade = "daylight" },
  { file = stagingDir .. "/IMG_E5122.HEIC", name = "me-18-trail", tall = true, grade = "daylight" }
}

project:SetSetting("timelineFrameRate", "24")

for index, pick in ipairs(picks) do
  local clips = mediaStorage:AddItemListToMediaPool({ pick.file })
  assert(clips and clips[1], "Unable to import " .. pick.file)

  local width = pick.tall and "1200" or "1600"
  local height = pick.tall and "1600" or "1200"
  project:SetSetting("timelineResolutionWidth", width)
  project:SetSetting("timelineResolutionHeight", height)

  local timeline = mediaPool:CreateTimelineFromClips(pick.name, { clips[1] })
  assert(timeline, "Unable to create timeline for " .. pick.name)
  project:SetCurrentTimeline(timeline)
  timeline:SetSetting("timelineResolutionWidth", width)
  timeline:SetSetting("timelineResolutionHeight", height)

  local items = timeline:GetItemListInTrack("video", 1)
  local item = items and items[1]
  assert(item, "No timeline item for " .. pick.name)

  local grade = grades[pick.grade]
  assert(item:SetCDL({
    NodeIndex = "1",
    Slope = grade.slope,
    Offset = grade.offset,
    Power = grade.power,
    Saturation = grade.saturation
  }), "Unable to apply CDL to " .. pick.name)

  item:SetProperty("Scaling", 2)
  if pick.rotation then
    item:SetProperty("RotationAngle", pick.rotation)
  end

  resolve:OpenPage("color")
  local stills = timeline:GrabAllStills(2)
  assert(stills and stills[1], "Unable to grab still for " .. pick.name)
  album:SetLabel(stills[1], pick.name)
  assert(album:ExportStills({ stills[1] }, outputDir, pick.name, "jpg"), "Unable to export " .. pick.name)

  print(string.format("[%02d/%02d] graded %s", index, #picks, pick.name))
end

projectManager:SaveProject()
print("DaVinci gallery grading complete: " .. outputDir)
