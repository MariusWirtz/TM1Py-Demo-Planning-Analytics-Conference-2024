import random

from TM1py import TM1Service, Dimension, Hierarchy, Element
from mdxpy import MdxBuilder, MdxHierarchySet

from constants import prod_params, dev_params


def prod_to_dev(cube_name: str, dimension_name: str):
    print(cube_name, dimension_name)
    with TM1Service(**prod_params) as tm1_prod:
        with TM1Service(**dev_params) as tm1_dev:
            customers = tm1_prod.elements.get_leaf_element_names(dimension_name, dimension_name)
            customer_mapping = dict()

            random.shuffle(customers)
            for c, customer in enumerate(customers):
                customer_mapping[customer] = "C" + str(c).zfill(4)

            hierarchy = tm1_prod.hierarchies.get(dimension_name, dimension_name)
            anon_hierarchy = Hierarchy(name=dimension_name, dimension_name=dimension_name)
            for element in hierarchy.elements.values():
                if element.element_type == Element.Types.CONSOLIDATED:
                    anon_hierarchy.add_element(element_name=element.name, element_type="Consolidated")
                else:
                    anon_hierarchy.add_element(element_name=customer_mapping[element.name], element_type="Numeric")
            for (parent, child), weight in hierarchy.edges.items():
                anon_hierarchy.add_edge(parent, customer_mapping.get(child, child), weight)
            anon_dimension = Dimension(name=dimension_name, hierarchies=[anon_hierarchy])

            tm1_dev.dimensions.update_or_create(anon_dimension)

            cube = tm1_prod.cubes.get(cube_name)
            for dimension_name in cube.dimensions:
                if dimension_name == "Customer":
                    continue
                dimension_name = tm1_prod.dimensions.get(dimension_name)
                tm1_dev.dimensions.update_or_create(dimension_name)
            tm1_dev.cubes.update_or_create(cube)

            query = MdxBuilder.from_cube("Sales").columns_non_empty()
            for dimension_name in tm1_prod.cubes.get_dimension_names(cube.name):
                query.add_hierarchy_set_to_column_axis(MdxHierarchySet.all_leaves(dimension_name, dimension_name))

            df = tm1_prod.cells.execute_mdx_dataframe(mdx=query.to_mdx())
            df["Customer"].replace(customer_mapping, inplace=True)
            tm1_dev.cells.write_dataframe(cube_name, df, use_blob=True)

            view = tm1_prod.views.get(cube_name, "Default")
            tm1_dev.views.update_or_create(view, private=False)
