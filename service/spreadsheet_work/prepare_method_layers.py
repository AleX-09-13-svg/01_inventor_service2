import json,re,pathlib
root=pathlib.Path(__file__).parent
rows=json.loads((root/'workbook_rows.json').read_text(encoding='utf-8'))
api='update active_document_name screen_updates_suspended pick show_message object_collection pick_part update_part save_part save_part_as parameter parameter_value add_user_parameter surface_body plane_geometry pick_face set_sketch_color_rgb reset_faces_to_feature_appearance add_sketch model_to_sketch_point sketch_to_model_points create_point2d create_point3d add_sketch_point project_point_to_plane project_entity_to_sketch add_sketch_line add_two_point_dimension add_aligned_dimension solve_sketch set_sketch_visible _add_geometric_constraint add_ground_constraint add_coincident_constraint add_symmetry_constraint create_work_plane_by_line_plane_angle add_offset_work_plane rename_sketch delete_sketch sketch_to_model_point add_sketch_circle add_sketch_arc add_parallel_constraint add_perpendicular_constraint set_sketch_defer_updates'.split()
app='build_part_config_from_excel refresh_linked_parameters_from_excel schedule_linked_parameters_refresh load_part_config apply_part_config apply_part_operation _apply_center_hole_on_selected_face add_holes add_counterbore_holes add_hole_batch add_counterbore_batch create_hole_batch_with_fallback ensure_drilling_sketch_parameters create_drilling_sketch create_drilling_sketches_for_faces add_face_center_point'.split()
mapping={x:'api' for x in api}|{x:'app' for x in app}
spec={'colors':{'api':'#D9EAF7','helper':'#FFF2CC','app':'#E2F0D9'},'fonts':{'api':'#156082','helper':'#9C6500','app':'#237A3B'},'cells':[],'mixed':[]}
for xml,sheet,col in [('xl/worksheets/sheet1.xml','Структура папок','B'),('xl/worksheets/sheet2.xml','Лист1',None)]:
 for row in rows[xml]:
  for addr,text in row.items():
   if (col and not addr.startswith(col)) or (not col and not addr.startswith(('B','C'))): continue
   matches=list(re.finditer(r'\b([A-Za-z_]\w*)\([^)]*\)',text))
   if not matches: continue
   cats=[mapping.get(m.group(1),'helper') for m in matches]
   entry={'sheet':sheet,'cell':addr,'text':text,'methods':[{ 'start':m.start(),'end':m.end(),'name':m.group(1),'category':cat} for m,cat in zip(matches,cats)]}
   if len(set(cats))==1: spec['cells'].append(entry|{'category':cats[0]})
   else: spec['mixed'].append(entry)
(root/'method_layers.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
print('Single-category cells:',len(spec['cells']),'Mixed:',len(spec['mixed']))
