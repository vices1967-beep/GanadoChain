#[starknet::contract]
mod GanadoRegistry {
    use starknet::ContractAddress;
    use starknet::get_caller_address;

    #[storage]
    struct Storage {
        admin: ContractAddress,
        next_lote_id: u128,
        lote_to_hash: LegacyMap::<u128, felt252>,      // lote_id -> data hash
        lote_to_address: LegacyMap::<u128, felt252>,   // lote_id -> btc address
    }

    #[event]
    #[derive(Drop, Debug)]
    enum Event {
        LoteCertified: LoteCertified,
    }

    #[derive(Drop, Debug, starknet::Event)]
    struct LoteCertified {
        lote_id: u128,
        btc_address: felt252,
        data_hash: felt252,
    }

    #[constructor]
    fn constructor(ref self: ContractState) {
        self.admin.write(get_caller_address());
        self.next_lote_id.write(1);
    }

    #[external]
    fn request_btc_certification(
        ref self: ContractState,
        btc_address: felt252,
        data_hash: felt252
    ) -> u128 {
        let lote_id = self.next_lote_id.read();
        self.next_lote_id.write(lote_id + 1);

        self.lote_to_hash.write(lote_id, data_hash);
        self.lote_to_address.write(lote_id, btc_address);

        self.emit(LoteCertified {
            lote_id,
            btc_address,
            data_hash,
        });

        lote_id
    }

    #[view]
    fn get_certification_data(self: @ContractState, lote_id: u128) -> (felt252, felt252) {
        let hash = self.lote_to_hash.read(lote_id);
        let addr = self.lote_to_address.read(lote_id);
        (hash, addr)
    }
}