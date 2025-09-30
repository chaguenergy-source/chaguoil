const _window = window
const backendURL = _window.__ENV && _window.__ENV.backendURL

// const axiosClient = axios.create({
//   baseURL: `${backendURL}`,
//   timeout: 20000,
//   withCredentials: true
// })


// const config = {
//   headers: {
//     "Content-Type": "application/json",
//     "Access-Control-Allow-Origin": "*"
//   }
// }

 function Shop() {

  // const [user, setUser] = useState(null)
  // const [showModal, setShowModal] = useState(false)

  const signIn = async () => {
    const scopes = ["username", "payments"]
    const authResult = await window.Pi.authenticate(
      scopes,
      onIncompletePaymentFound
    )
    // signInUser(authResult)
    // setUser(authResult.user)
  }

  // const signOut = () => {
  //   setUser(null)
  //   signOutUser()
  // }

  // const signInUser = authResult => {
  //   axiosClient.post("/user/signin", { authResult })
  //   return setShowModal(false)
  // }

  // const signOutUser = () => {
  //   return axiosClient.get("/user/signout")
  // }

  // const onModalClose = () => {
  //   setShowModal(false)
  // }

  const orderProduct = async (memo, amount, paymentMetadata) => {

    // if (user === null) {
    //   return setShowModal(true)
    // }
    const paymentData = { amount, memo, metadata: paymentMetadata }
    const callbacks = {
      onReadyForServerApproval,
      onReadyForServerCompletion,
      onCancel,
      onError
    }
    const payment = await window.Pi.createPayment(paymentData, callbacks)
    console.log(payment)
  }

  const onIncompletePaymentFound = payment => {
    console.log("onIncompletePaymentFound", payment)
    // return axiosClient.post("/payments/incomplete", { payment })
  }

  const onReadyForServerApproval = paymentId => {
    console.log("onReadyForServerApproval", paymentId)
    // axiosClient.post("/payments/approve", { paymentId }, config)
  }

  const onReadyForServerCompletion = (paymentId, txid) => {
    console.log("onReadyForServerCompletion", paymentId, txid)
    // axiosClient.post("/payments/complete", { paymentId, txid }, config)
  }

  const onCancel = paymentId => {
    console.log("onCancel", paymentId)
    // return axiosClient.post("/payments/cancelled_payment", { paymentId })
  }

  const onError = (error, payment) => {
    console.log("onError", error)
    if (payment) {
      console.log(payment)
      // handle the error accordingly
    }
  }
}