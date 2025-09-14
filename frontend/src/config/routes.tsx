import { Routes, Route } from 'react-router-dom'

function Home() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <h1 className="text-4xl font-bold text-primary-600">
        GanadoChain - Funcionando!
      </h1>
    </div>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  )
}

export default AppRoutes