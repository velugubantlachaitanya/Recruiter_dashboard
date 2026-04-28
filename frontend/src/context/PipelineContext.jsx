import { createContext, useContext, useState } from 'react'

const PipelineContext = createContext(null)

export function PipelineProvider({ children }) {
  const [parsedJD, setParsedJD]     = useState(null)
  const [rawJD, setRawJD]           = useState('')
  const [candidates, setCandidates] = useState([])
  const [shortlist, setShortlist]   = useState([])
  const [engagedMap, setEngagedMap] = useState({})

  function resetPipeline() {
    setParsedJD(null)
    setRawJD('')
    setCandidates([])
    setShortlist([])
    setEngagedMap({})
  }

  return (
    <PipelineContext.Provider value={{
      parsedJD, setParsedJD,
      rawJD, setRawJD,
      candidates, setCandidates,
      shortlist, setShortlist,
      engagedMap, setEngagedMap,
      resetPipeline,
    }}>
      {children}
    </PipelineContext.Provider>
  )
}

export const usePipeline = () => useContext(PipelineContext)
