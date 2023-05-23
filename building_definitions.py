import collections
import geolocation

BuildingDef = collections.namedtuple(
	"BuildingDef",
	["latitude","longitude","name"])

buildings=[
	BuildingDef(
		latitude=37.56098713306348, 
		longitude=126.9350676160249,
		name="공학원"),
	BuildingDef(
		latitude=37.56082501621413, 
		longitude=126.93582759114835,
		name="공학원"),
	BuildingDef(
		latitude=37.561477325183965, 
		longitude=126.93596955291314,
		name="제1공학관"),
	BuildingDef(
		latitude=37.56218007992962, 
		longitude=126.93624260527221,
		name="제1공학관"),
	BuildingDef(
		latitude=37.56173031643782, 
		longitude=126.93657948873086,
		name="제1공학관"),
	BuildingDef(
		latitude=37.561842757551894, 
		longitude=126.93603692851528,
		name="제4공학관"),
	BuildingDef(
		latitude=37.56179715299392, 
		longitude=126.93483686779197,
		name="제3공학관"),
	BuildingDef(
		latitude=37.56169915799498, 
		longitude=126.9353931644921, 
		name="제3공학관"),
	BuildingDef(
		latitude=37.562394919009115,
		longitude= 126.93486159107138,
		name="제2공학관"),
	BuildingDef(
		latitude=37.56228222451999, 
		longitude=126.93546425071348, 
		name="제2공학관"),
	BuildingDef(
		latitude=37.56269729859164, 
		longitude=126.9355440191072,
		name="스포츠과학관"),
	BuildingDef(
		latitude=37.56320251663343, 
		longitude=126.93521924211872,
		name="체육교육관"),
	BuildingDef(
		latitude=37.56321231573954, 
		longitude=126.93479274685593,
		name="과학원"),
	BuildingDef(
		latitude=37.56352099207399, 
		longitude=126.93454241039882,
		name="과학원"),
	BuildingDef(
		latitude=37.56369737691681, 
		longitude=126.93586207365126 ,
		name="학술정보관"),
	BuildingDef(
		latitude=37.5641701867306, 
		longitude=126.9353366828054, 
		name="과학관"),
	BuildingDef(
		latitude=37.564032997667276, 
		longitude=126.9347711124266, 
		name="과학관"),
	BuildingDef(
		latitude=37.56395950118607, 
		longitude=126.93428589708479, 
		name="과학관"),
	BuildingDef(
		latitude=37.56347199281631, 
		longitude=126.93390885224085, 
		name="첨단과학기술연구관"),
	BuildingDef(
		latitude=37.563102075730136, 
		longitude=126.93399538935653, 
		name="첨단과학기술연구관"),
	BuildingDef(
		latitude=37.56300898314713, 
		longitude=126.93431371246193, 
		name="IBS관"),
	BuildingDef(
		latitude=37.56277379867469, 
		longitude=126.9331393095379,
		name="GS칼텍스산학협력관")
	]
	

	
BuildingLGC= collections.namedtuple(
	"BuildingLGC",
	["lgc","name"])
buildings_lgc=[]
for b in buildings:
	buildings_lgc.append(
		BuildingLGC(
			lgc=geolocation.LocalGroundCoordinates.from_lla(
				latitude=b.latitude,
				longitude=b.longitude,
				altitude=0),
			name=b.name))

