fn scene_dummyclean=(
	to_delete = #()
	for obj in objects do(
		if classOf obj == Dummy do(
			append to_delete obj
		)
	)
	for del_obj in to_delete do delete del_obj
)

/*-- Define o nome do material
materialName = "Teste"

-- Cria um novo material Corona
teste = CoronaMtl()

-- Define as propriedades do material
teste.colorDiffuse = color 10 100 0 -- Define a cor difusa (RGB)
teste.reflectGlossiness = 0.8 -- Define a reflexão e a suavidade

-- Atribui o nome do material
teste.name = materialName

-- Aplica o material a uma seleção de objetos
$Box001.material = teste
teste.name = $Box001.name

-- Adiciona o material à biblioteca de materiais do 3ds Max
--addMaterialToScene teste
--showProperties(teste)
*/
fn create_sky = (
    hdri_sky = CoronaSky cloudsEnable:true intensityMultiplier:0.1
    IMXR_sun = CoronaSun name:"IMXRSun" on:true targeted:true sizeMultiplier:2 intensity:0.2 shadowsFromClouds:true textured:true
    IMXR_sun.position = [500, 500, 500]
)



fn change_sun_target=(
	sun_target = getNodeByName "IMXRSun.Target"
	sun_target.position = [0, 0, 0]
)


scene_dummyclean()
create_sky()
change_sun_target()
