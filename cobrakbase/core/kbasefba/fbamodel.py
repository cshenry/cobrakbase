from cobra.core import Model
from cobrakbase.core.kbaseobject import KBaseObject
from cobrakbase.core.kbasebiochem.media import Media


class FBAModel(KBaseObject, Model):

    def __init__(self, data=None, info=None, args=None, kbase_type=None):
        KBaseObject.__init__(self, data, info, args, kbase_type)
        Model.__init__(self, self.data['id'], self.data['name'])

    def get_exchange_by_metabolite_id(self, metabolite_id):
        return list(filter(lambda x: list(x.metabolites)[0].id == metabolite_id, self.exchanges))

    @Model.medium.setter
    def medium(self, medium):
        """Get or set the constraints on the model exchanges.

        `model.medium` returns a dictionary of the bounds for each of the
        boundary reactions, in the form of `{rxn_id: bound}`, where `bound`
        specifies the absolute value of the bound in direction of metabolite
        creation (i.e., lower_bound for `met <--`, upper_bound for `met -->`)

        Parameters
        ----------
        medium: dictionary-like
            The medium to initialize. medium should be a dictionary defining
            `{rxn_id: bound}` pairs.

            or

            KBase Media object enconding medium
        """
        for exchange_reaction in self.exchanges:
            exchange_reaction.lower_bound = 0
        if type(medium) == Media:
            in_model = dict(filter(lambda x: x[0] in self.metabolites, medium.get_media_constraints().items()))
            for compound_id in in_model:
                for exchange_reaction in self.get_exchange_by_metabolite_id(compound_id):
                    exchange_reaction.lower_bound, exchange_reaction.upper_bound = in_model[compound_id]
        else:
            Model.medium.fset(self, medium)

    def build_peakstring(self,link,additional_peak_hash = {}):
        peakstring_hash = dict()
        for met in self.modelcompounds:
            if hasattr(met,'dblinks'):
                if link in met.dblinks:
                    array = met.dblinks[link]
                    for form in array:
                        if form not in peakstring_hash:
                            peakstring_hash[form] = list()
                        peakstring_hash[form].append(met.id)
        for peak in additional_peak_hash:
            if peak not in peakstring_hash:
                peakstring_hash[peak] = list()
            for cpd in additional_peak_hash[peak]:
                if cpd not in peakstring_hash[peak]:
                    peakstring_hash[peak].append(cpd)
        print(len(peakstring_hash))
        peakstring = ""
        for form in peakstring_hash:
            peakstring += form+":1"
            for cpd in peakstring_hash[form]:
                peakstring += ":"+cpd
            peakstring += ";"
        return peakstring