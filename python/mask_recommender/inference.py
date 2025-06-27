# Gibbs Sampling strategy
# For those variables not in the set of evidence, sample initial set of values
# Then sample each one, using the neighbors. Use some arbitrary fixed ordering (e.g. topological sort?)
#   Let's call the variable to be sampled as the "target."
#   To sample a target, combine the factors.
#   Sum over nuisance variables
#   Sample using multinomial distribution.
#
# Once all the non-evidence variables are sampled, this constitutes the first sample.
# Rinse and repeat until we have enough samples


class Node():
    def __init__(self, name):
        self.name = name

    def add_parents(self, parents):
        self.parents = parents

class DirectedEdge():
    def __init__(self, from_name, to_name):
        self.from_name = from_name
        self.to_name = to_name

class ConditionalProbabilityTable():
    def __init__(self, data, node, parents):
        self.data = data
        self.node = node
        self.parents = parents

class Factor():
    def __init__(self, table):
        self.table = table
        self.variable_names = list(set(table.columns) - {'value'})

    def times(self, factor):
        common_variables = list(set(self.variable_names).intersection(set(factor.variable_names)))

        assert len(common_variables) == 1

        new_table = self.table.merge(factor.table, on=common_variables[0], suffixes=('_left', '_right'))
        new_table['value'] = new_table['value_left'] * new_table['value_right']
        return Factor(new_table.drop(columns=['value_left', 'value_right']))

    def __str__(self):
        return str(self.table)

