from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class FakeToolModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self
