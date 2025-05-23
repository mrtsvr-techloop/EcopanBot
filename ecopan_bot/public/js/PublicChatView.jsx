import {
  Flex,
  IconButton,
  VStack,
  Box,
  Card,
  CardBody,
  Avatar,
  useToast,
  Textarea,
  Text,
  Heading,
} from "@chakra-ui/react";
import { SendIcon } from "lucide-react";
import React, { useState, useEffect } from "react";
import Message from "./components/message/Message";

const PublicChatView = ({ sessionID }) => {
  const toast = useToast();
  const [promptMessage, setPromptMessage] = useState("");
  const [messages, setMessages] = useState([]);
  
  // Carica i messaggi dal localStorage
  useEffect(() => {
    const storedMessages = localStorage.getItem(`ecopanbot_messages_${sessionID}`);
    if (storedMessages) {
      setMessages(JSON.parse(storedMessages));
    } else {
      setMessages([{
        from: "ai",
        isLoading: false,
        content: "Ciao! Sono ecopanBot. Come posso aiutarti oggi?",
      }]);
    }
  }, [sessionID]);

  // Salva i messaggi nel localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`ecopanbot_messages_${sessionID}`, JSON.stringify(messages));
    }
  }, [messages, sessionID]);

  const handleSendMessage = () => {
    if (!promptMessage.trim().length) {
      return;
    }

    setMessages((old) => [
      ...old,
      { from: "human", content: promptMessage, isLoading: false },
      { from: "ai", content: "", isLoading: true },
    ]);
    setPromptMessage("");

    // Usa fetch per chiamare l'API
    fetch('/api/method/ecopan_bot.api.get_chatbot_response', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        prompt_message: promptMessage,
        session_id: sessionID,
      }),
    })
    .then(response => response.json())
    .then(data => {
      setMessages((old) => {
        const updated = [...old];
        updated[updated.length - 1] = {
          from: "ai",
          content: data.message,
          isLoading: false,
        };
        return updated;
      });
    })
    .catch((e) => {
      console.error(e);
      setMessages((old) => {
        const updated = [...old];
        updated[updated.length - 1] = {
          from: "ai",
          content: "Mi dispiace, si è verificato un errore. Riprova più tardi.",
          isLoading: false,
        };
        return updated;
      });
      
      toast({
        title: "Errore di comunicazione",
        description: "Non è stato possibile ottenere una risposta dal server.",
        status: "error",
        position: "bottom-right",
        duration: 5000,
      });
    });
  };

  return (
    <Flex
      direction={"column"}
      height={"100%"}
      width={"100%"}
      maxWidth={"4xl"}
      mx={"auto"}
    >
      <Heading as="h1" size="lg" mb={4} textColor={"gray.700"}>
        ecopanBot - Assistente Virtuale
      </Heading>
      
      {/* Chat Area */}
      <Box
        width={"100%"}
        height={"70%"}
        overflowY="scroll"
        shadow={"md"}
        rounded={"md"}
        backgroundColor={"white"}
        mb={4}
      >
        <VStack spacing={2} align="stretch" p={4}>
          {messages.map((message, index) => (
            <Message key={`${index}-${Date.now()}`} message={message} />
          ))}
        </VStack>
      </Box>

      {/* Prompt Area */}
      <Card>
        <CardBody>
          <Flex gap={3} alignItems={"start"}>
            <Avatar name={"Utente"} size={"sm"} />
            <Textarea
              value={promptMessage}
              onChange={(event) => setPromptMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.code === "Enter" && !event.shiftKey && promptMessage) {
                  event.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Scrivi il tuo messaggio qui..."
              resize="none"
            />
            <IconButton
              aria-label="Invia messaggio"
              icon={<SendIcon height={16} />}
              onClick={handleSendMessage}
              isDisabled={!promptMessage.trim().length}
            />
          </Flex>
        </CardBody>
      </Card>
    </Flex>
  );
};

export default PublicChatView;