import Spinner from 'react-bootstrap/Spinner'
import '../styles/Loader.css'

function Loading() {
  return <Spinner animation="grow" className='spinner' variant='primary' />
}

export default Loading;