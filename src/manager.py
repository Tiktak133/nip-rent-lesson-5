from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key, year=0, month=0):
        costs = 0
        if apartment_key not in self.apartments:
            return None
        
        for bill in self.bills:
            if bill.apartment == apartment_key and (bill.settlement_year == year or year == 0) and (bill.settlement_month == month or month == 0):
                costs += bill.amount_pln        
        return costs
    
    def get_tenant_rents(self, tenant_key, year=0, month=0):
        rents = 0
        if tenant_key not in self.tenants:
            return None
        
        for tenant in self.tenants:
            if tenant.apartment == self.tenants[tenant_key].apartment and (tenant.settlement_year == year or year == 0) and (tenant.settlement_month == month or month == 0):
                rents += tenant.amount_pln        
        return rents
    

    
    def create_apartment_settlement(self, apartment_key, year, month):
        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_bills_pln=self.get_apartment_costs(apartment_key, year, month),
            total_rent_pln=self.get_tenant_rents(apartment_key, year, month),
            #total_due_pln=self.get_apartment_costs(apartment_key, year, month) - self.get_transfers_sum_for_apartment(apartment_key, year, month)
        )