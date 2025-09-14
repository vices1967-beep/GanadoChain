import { useState } from 'react'
import { connectToPolygonAmoy } from '@/utils/blockchain/web3'

function WalletConnect() {
  const [isConnected, setIsConnected] = useState(false)
  const [address, setAddress] = useState('')

  const handleConnect = async () => {
    try {
      const { address: connectedAddress } = await connectToPolygonAmoy()
      setIsConnected(true)
      setAddress(connectedAddress)
    } catch (error) {
      console.error('Error connecting wallet:', error)
    }
  }

  return (
    <div className="flex items-center space-x-4">
      {isConnected ? (
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm text-gray-600 font-mono">
            {address.slice(0, 6)}...{address.slice(-4)}
          </span>
        </div>
      ) : (
        <button
          onClick={handleConnect}
          className="btn-secondary"
        >
          Conectar Wallet
        </button>
      )}
    </div>
  )
}

export default WalletConnect