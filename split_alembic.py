import hou

def split_alembic_meshes():
    alembic_dict = {}
    nodes = hou.selectedNodes()
    if nodes:
        # parse selection for either alembics or geo with alembic children to capture all selected alembic nodes
        for node in nodes:
            if node.type().name() == 'alembic':
                alembic_dict[node.name()] = {'node': node, 
                                             'parent': node.parent(), 
                                             'position': node.position(), 
                                             'parent_position': node.parent().position(), 
                                             'path': node.parm('fileName').eval()}
            elif node.type().name() == 'geo':
                kids = node.children()
                for kid in kids:
                    if kid.type().name() == 'alembic':
                        alembic_dict[kid.name()] = {'node': kid, 
                                                    'parent': kid.parent(), 
                                                    'position': kid.position(), 
                                                    'parent_position': kid.parent().position(), 
                                                    'path': kid.parm('fileName').eval()}
        if alembic_dict:
            for name, node_dict in alembic_dict.iteritems():
                node_dict['node'].parm('groupnames').set(3)
                groups = [g.name() for g in node_dict['node'].geometry().primGroups()]
                for i, group_name in enumerate(groups, 1):
                    # create blast, set to group only
                    if hou.node("/".join(["/obj",node_dict['parent'].name(),group_name])):
                        hou.node("/".join(["/obj",node_dict['parent'].name(),group_name])).destroy()
                    blast = hou.node("/obj/"+node_dict['parent'].name()).createNode("blast", node_name=group_name)
                    blast.setInput(0, node_dict['node'])
                    blast.parm('group').set(group_name)
                    blast.parm('negate').set(True)
                    x_position = (node_dict['position'][0]+i*2) - len(groups)
                    blast.setPosition((x_position, node_dict['position'][1]-1))
                    # create OUT null for blast
                    if hou.node("/".join(["/obj",node_dict['parent'].name(),'OUT_'+group_name])):
                        hou.node("/".join(["/obj",node_dict['parent'].name(),'OUT_'+group_name])).destroy()
                    null = hou.node("/obj/"+node_dict['parent'].name()).createNode("null", node_name='OUT_'+group_name)
                    null.setInput(0, blast)
                    null.setPosition((x_position, node_dict['position'][1]-2))
                    # create external geo for each group
                    if hou.node("/".join(["/obj", group_name])):
                        hou.node("/".join(["/obj", group_name])).destroy()
                    geo = hou.node("/obj/").createNode("geo", node_name=group_name)
                    geo.setPosition((node_dict['parent_position'][0], node_dict['parent_position'][1]-i))
                    # create object merge inside each geo to bring in each isolated geo from nulls
                    if hou.node("/".join(["/obj", group_name, group_name+'_merge'])):
                        hou.node("/".join(["/obj", group_name, group_name+'_merge'])).destroy()
                    merge = hou.node("/obj/"+geo.name()).createNode("object_merge", node_name=group_name+'_merge')
                    merge.parm("objpath1").set("/".join(["/obj",node_dict['parent'].name(),'OUT_'+group_name]))
        else:
            print('You must select either a geo with a child alembic SOP or an alembic SOP directly.')
    else:
        print('Nothing selected')
