import Spinner from 'react-bootstrap/Spinner';
import '../styles/Loader.css'

function ScreenLoader() {
  return <Spinner animation="grow" variant="primary" className='spinner'/>;
}

export default ScreenLoader;