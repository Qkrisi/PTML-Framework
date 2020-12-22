const socket = new WebSocket(`ws://${document.location.hostname}:${WSPort}`)

class PTMLError extends Error {}

socket.onmessage = event => {
        let message = event.data
        let splitted = message.split(" ")
        let instruction = splitted[0]
        let arguments = splitted.slice(1)
        switch(instruction)
        {
                case "eval":
                        eval(arguments.join(" "))
                        break
                case "throw":
                        throw new PTMLError(arguments.join(" "))
                        break
                case "create":
                        document.body.innerHTML += arguments.join(" ")          //TODO: Make parenting work
                        break
                case "ChangeInner":
                        let id = arguments[0]
                        arguments = arguments.slice(1)
                        let element = document.getElementsByClassName(`ptml-id-${id}`)
                        if(element.length>0) element[0].innerHTML = arguments.join(" ")
                        break
                default:
                        console.log(`Got unknown instruction: ${instruction}`)
                        break
        }
}
