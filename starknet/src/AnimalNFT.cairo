#[starknet::contract]
mod AnimalNFT {
    use starknet::ContractAddress;
    use starknet::get_caller_address;

    #[storage]
    struct Storage {
        next_token_id: u128,
        token_owner: LegacyMap<u128, ContractAddress>,
        token_uri: LegacyMap<u128, felt252>,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        AnimalCreated: AnimalCreated,
    }

    #[derive(Drop, starknet::Event)]
    struct AnimalCreated {
        token_id: u128,
        owner: ContractAddress,
        metadata_hash: felt252,
    }

    #[constructor]
    fn constructor(ref self: ContractState) {
        self.next_token_id.write(1);
    }

    #[external(v0)]
    fn create_animal(ref self: ContractState, metadata_hash: felt252) -> u128 {
        let caller = get_caller_address();
        let token_id = self.next_token_id.read();
        
        self.next_token_id.write(token_id + 1);
        self.token_owner.write(token_id, caller);
        self.token_uri.write(token_id, metadata_hash);
        
        self.emit(AnimalCreated { 
            token_id: token_id,
            owner: caller, 
            metadata_hash: metadata_hash,
        });
        
        token_id
    }

    #[external(v0)]
    fn owner_of(self: @ContractState, token_id: u128) -> ContractAddress {
        self.token_owner.read(token_id)
    }

    #[external(v0)]
    fn token_uri(self: @ContractState, token_id: u128) -> felt252 {
        self.token_uri.read(token_id)
    }
}