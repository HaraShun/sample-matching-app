import { AIConversation } from "@aws-amplify/ui-react-ai";
import { Authenticator } from "@aws-amplify/ui-react";
import { Card, View, Flex, Heading, Divider, Avatar, Button } from "@aws-amplify/ui-react";
import { useAIConversation } from "./client";
import "./App.css";

function App() {
  const [
    {
      data: { messages },
      isLoading,
    },
    handleSendMessage,
  ] = useAIConversation("chat");

  function Header({ signOut }: any) {
    return (
      <View
        position="fixed"
        width="100%"
        backgroundColor="white"
        top="0"
        left="0"
        padding="2rem"
      >
        <Flex
          direction="row"
          justifyContent="space-between"
        >
          <Heading level={3}>Matching Chat アプリ</Heading>
          <Button
            variation="link"
            onClick={signOut}
          >
            Sign out
          </Button>
        </Flex>
        <Divider />
      </View>
    )
  }

  function WellcomeMessageCard() {
    return (

      <Card>
        <Heading level={4}>こんにちは！<br /><br />あなたの「出身地」,「学生時代の部活」,「趣味」,「好きな映画・ドラマ」,「好きな料理ジャンル」,「休日の過ごし方」,「大学の学部」等を入力してみてください。<br />相性の良い人をレコメンドします。</Heading>

        <Heading level={5}><br />【入力例】<br />部署は公共事業部、出身地は東京、学生時代の部活はテニス部、趣味はサッカー観戦、好きな映画はクリストファー・ノーラン作品、好きな料理はラーメン、休日の過ごし方は子どもと遊ぶこと、大学時代は商学部、です。相性の良い人をレコメンドして。</Heading>
      </Card>

    )
  }

  return (
    <Authenticator>
      {({ signOut }) => (
        <Card width="100%" height="100%" display="flex" style={{ justifyContent: "center" }}>
          <Header signOut={signOut} />
          <AIConversation
            messages={messages}
            isLoading={isLoading}
            handleSendMessage={handleSendMessage}
            welcomeMessage={
              <WellcomeMessageCard />
            }
            displayText={{
              getMessageTimestampText: (date) => new Intl.DateTimeFormat('ja-JP', {
                dateStyle: 'full',
                timeStyle: 'short',
                hour12: true,
                timeZone: 'Asia/Tokyo'
              }).format(date)
            }}
            avatars={{
              user: {
                avatar: <Avatar src="/man_icon.jpg" />,
                username: "あなた",
              },
              ai: {
                avatar: <Avatar src="/ai_icon.jpg" />,
                username: "AI"
              }
            }}
          />
        </Card>
      )}

    </Authenticator>
  )
}

export default App
