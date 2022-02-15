df = df.astype({'longitude':'float64','latitude':'float64','tree_number':'object', 'crown_width':'Int64','number_of_stems':'Int64','dbh':'float64',
                                        'hard_surface':'Int64','height_to_crown_base':'Int64','total_height':'Int64','reduced_crown':'Int64','unbalanced_crown':'Int64',
                                        'defoliation':'Int64','weak_or_yellow_foliage':'Int64','dead_or_broken_branch':'Int64','lean':'Int64',
                                        'poor_branch_attachment':'Int64','branch_scars':'Int64','trunk_scars':'Int64','conks':'Int64','branch_rot_or_cavity':'Int64',
                                        'trunk_rot_or_cavity':'Int64','confined_space':'Int64','crack':'Int64','girdling_roots':'Int64', 'exposed_roots':'Int64',
                                        'recent_trenching':'Int64','cable_or_brace':'Int64','demerits':'Int64','cpa':'Int64', 'rdbh':'Int64',})
