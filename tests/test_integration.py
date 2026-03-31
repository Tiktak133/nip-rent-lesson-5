import pytest
from src import manager
from src.models import Apartment
from src.manager import Manager
from src.models import ApartmentSettlement, Parameters


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key

def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names

def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True

    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False
    
def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 760.0 + 150.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0 # nie powinno być żadnych kosztów, bo nie ma żadnych rachunków z tym okresem rozliczeniowym
    assert manager.get_apartment_costs('apartament-invalid', 2025, 1) == None


def test_create_apartment_settlement_returns_total_due_from_bills_and_rent():
    parameters = Parameters()
    manager = Manager(parameters)

    styczen_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    luty_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 2)

    assert isinstance(styczen_settlement, ApartmentSettlement)
    assert styczen_settlement.apartment == 'apart-polanka'
    assert styczen_settlement.year == 2025
    assert styczen_settlement.month == 1
    assert styczen_settlement.total_rent_pln == 4200.0
    assert styczen_settlement.total_bills_pln == 910.0
    assert styczen_settlement.total_due_pln == 5110.0

    assert isinstance(luty_settlement, ApartmentSettlement)
    assert luty_settlement.apartment == 'apart-polanka'
    assert luty_settlement.year == 2025
    assert luty_settlement.month == 2
    assert luty_settlement.total_rent_pln == 4200.0
    assert luty_settlement.total_bills_pln == 0.0
    assert luty_settlement.total_due_pln == 4200.0


def test_create_tenant_settlements_splits_bills_for_multiple_single_and_zero_tenants():
    # 2+ tenants scenario
    manager_many = Manager(Parameters())
    apartment_settlement_many = manager_many.create_apartment_settlement('apart-polanka', 2025, 1)
    tenant_settlements_many = manager_many.create_tenant_settlements(apartment_settlement_many)

    assert len(tenant_settlements_many) == 3
    assert {s.tenant for s in tenant_settlements_many} == {'tenant-1', 'tenant-2', 'tenant-3'}
    assert all(s.apartment_settlement == 'apart-polanka' for s in tenant_settlements_many)
    assert all(s.month == 1 for s in tenant_settlements_many)
    assert all(s.year == 2025 for s in tenant_settlements_many)
    assert all(s.bills_pln == pytest.approx(910.0 / 3) for s in tenant_settlements_many)
    assert sum(s.bills_pln for s in tenant_settlements_many) == pytest.approx(910.0)

    # 1 tenant scenario
    manager_one = Manager(Parameters())
    manager_one.tenants = {
        'tenant-1': manager_one.tenants['tenant-1']
    }
    apartment_settlement_one = manager_one.create_apartment_settlement('apart-polanka', 2025, 1)
    tenant_settlements_one = manager_one.create_tenant_settlements(apartment_settlement_one)

    assert len(tenant_settlements_one) == 1
    assert tenant_settlements_one[0].tenant == 'tenant-1'
    assert tenant_settlements_one[0].bills_pln == pytest.approx(910.0)
    assert tenant_settlements_one[0].month == 1
    assert tenant_settlements_one[0].year == 2025

    # 0 tenants scenario
    manager_zero = Manager(Parameters())
    manager_zero.tenants = {}
    apartment_settlement_zero = manager_zero.create_apartment_settlement('apart-polanka', 2025, 1)
    tenant_settlements_zero = manager_zero.create_tenant_settlements(apartment_settlement_zero)

    assert isinstance(tenant_settlements_zero, list)
    assert tenant_settlements_zero == []