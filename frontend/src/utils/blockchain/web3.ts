import { ethers } from 'ethers'
import { POLYGON_AMOY_PARAMS } from '@/config/blockchain'

export const connectToPolygonAmoy = async () => {
  if (typeof window.ethereum !== 'undefined') {
    try {
      // Solicitar conexión de cuenta
      await window.ethereum.request({ 
        method: 'eth_requestAccounts' 
      })

      // Agregar Polygon Amoy si no está presente
      try {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [POLYGON_AMOY_PARAMS],
        })
      } catch (addError) {
        console.log('Polygon Amoy ya está agregado o usuario rechazó')
      }

      // Cambiar a Polygon Amoy
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: POLYGON_AMOY_PARAMS.chainId }],
      })

      const provider = new ethers.BrowserProvider(window.ethereum)
      const signer = await provider.getSigner()
      const address = await signer.getAddress()

      return { provider, signer, address, connected: true }
    } catch (error) {
      console.error('Error connecting to Polygon Amoy:', error)
      throw error
    }
  } else {
    throw new Error('MetaMask no está instalado')
  }
}

export const getCurrentNetwork = async () => {
  if (typeof window.ethereum !== 'undefined') {
    const chainId = await window.ethereum.request({ method: 'eth_chainId' })
    return chainId
  }
  return null
}