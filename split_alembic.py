import hou

def split_alembic_to_children():
    nodes = hou.selectedNodes()
    if nodes:
        alembic_node = hou.selectedNodes()[0]
        if alembic_node.type().name() == 'alembic':
            position = alembic_node.position()
            alembic_parent = alembic_node.parent()
            parent_position = alembic_parent.position()
            alembic_node.parm('groupnames').set(3)
            groups = [g.name() for g in alembic_node.geometry().primGroups()]
            for i, g in enumerate(groups, 1):
                # first create blasts and NULLS internally, then create external object merges
                blast = hou.node("/obj/"+alembic_parent.name()).createNode("blast", node_name=g)
                blast.setInput(0, alembic_node)
                blast.parm('group').set(g)
                blast.parm('negate').set(True)
                x_position = (position[0]+i*2) - len(groups)
                blast.setPosition((x_position, position[1]-1))
                null = hou.node("/obj/"+alembic_parent.name()).createNode("null", node_name='OUT_'+g)
                null.setInput(0, blast)
                null.setPosition((x_position, position[1]-2))
                geo = hou.node("/obj/").createNode("geo", node_name=g)
                geo.setPosition((parent_position[0], parent_position[1]-i))
                merge = hou.node("/obj/"+geo.name()).createNode("object_merge", node_name=g+'_merge')
                merge.parm("objpath1").set("/".join(["/obj",alembic_parent.name(),'OUT_'+g]))
        else:
            print('You must select an alembic SOP to execute.')
    else:
        print('Nothing selected')
